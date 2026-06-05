"""
ChatGPT Web Bridge — Servidor API compatible con OpenAI.

Uso:
    python server.py --port 9090           # visible
    python server.py --port 9090 --no-headless  # invisible
"""

import sys
import time
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

from models import (
    ChatCompletionRequest, ChatCompletionResponse,
    ChatChoice, ChatMessage, UsageInfo,
    ModelInfo, ModelsListResponse,
    HealthResponse, ComponentStatus,
)
from chatgpt_bridge import ChatGPTBridge
from routes import router as v1_router
from health_diagnostics import diagnose, set_start_time
from chat_handler import process_chat, stream_chat

# v2.0 — Reliability
from queue_manager import RequestQueue, QueueFullError, QueueTimeoutError
from rate_limiter import RateLimiter
from error_codes import error_response
from graceful_shutdown import GracefulShutdown, ShuttingDownError
from watchdog import Watchdog
from session_recovery import SessionRecovery


# ═══════════════════════════════════════════════════════════
# Config
# ═══════════════════════════════════════════════════════════

BRIDGE: ChatGPTBridge = None  # type: ignore
HEADLESS = True
PORT = 9090
QUEUE: RequestQueue = RequestQueue(max_concurrent=1, max_queue=10)
LIMITER: RateLimiter = RateLimiter(rpm=10, burst=3)
SHUTDOWN: GracefulShutdown = GracefulShutdown(timeout=30.0)
WATCHDOG: Watchdog = None  # type: ignore
SESSION_RECOVERY: SessionRecovery = None  # type: ignore

AVAILABLE_MODELS = [
    ModelInfo(id="gpt-4o", created=1715367049, owned_by="chatgpt-web"),
    ModelInfo(id="gpt-4o-mini", created=1715367050, owned_by="chatgpt-web"),
    ModelInfo(id="o3", created=1735680000, owned_by="chatgpt-web"),
    ModelInfo(id="o4-mini", created=1735680001, owned_by="chatgpt-web"),
    ModelInfo(id="gpt-4.1", created=1740000000, owned_by="chatgpt-web"),
]


# ═══════════════════════════════════════════════════════════
# Lifecycle
# ═══════════════════════════════════════════════════════════

_start_time: float = 0.0


@asynccontextmanager
async def lifespan(app: FastAPI):
    global BRIDGE, WATCHDOG, SESSION_RECOVERY
    import time as _time
    _start_time = _time.time()
    banner()
    BRIDGE = await ChatGPTBridge(headless=HEADLESS).start()

    # Session recovery
    page = BRIDGE._browser.page if hasattr(BRIDGE, '_browser') else None
    SESSION_RECOVERY = SessionRecovery(BRIDGE._browser._context) if page else None

    # Watchdog
    if page:
        async def _recover():
            await page.reload(wait_until="domcontentloaded")
        WATCHDOG = Watchdog(page, on_recovery=_recover)
        await WATCHDOG.start()

    if not BRIDGE.is_authenticated:
        await _wait_for_login()
    SHUTDOWN.register_signals()
    print(f"\n✅ Bridge listo! API activa (cola:{QUEUE._max_queue} rpm:{LIMITER._rate*60:.0f}).\n")
    yield
    print("\n🛑 Apagando...")
    if WATCHDOG:
        await WATCHDOG.stop()
    if SESSION_RECOVERY:
        await SESSION_RECOVERY.save()
    await SHUTDOWN.wait_for_drain()
    await BRIDGE.stop()
    print("\n👋 Bridge cerrado.\n")


def banner():
    print(f"\n{'='*55}")
    print("  🤖 ChatGPT Web Bridge — OpenAI-Compatible API")
    print(f"{'='*55}")
    print(f"  Modo: {'HEADLESS' if HEADLESS else 'VISIBLE (debug)'}")
    print(f"  URL:  http://localhost:{PORT}/v1")
    print(f"{'='*55}\n")


async def _wait_for_login():
    print("\n⚠️  No detectado login en ChatGPT.")
    print("   Haz login en el navegador abierto,")
    print("   luego presiona Enter aquí para continuar...\n")
    await asyncio.get_event_loop().run_in_executor(None, input)
    # auth.ensure se llama dentro de bridge.send()


app = FastAPI(title="ChatGPT Web Bridge", version="1.8.0", lifespan=lifespan)
app.include_router(v1_router)


# ═══════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════

def _last_user_text(messages: list) -> str:
    """Extrae el texto del último mensaje user (incluso si es multimodal)."""
    for m in reversed(messages):
        role = m.get("role") if isinstance(m, dict) else m.role
        content = m.get("content", "") if isinstance(m, dict) else m.content
        if role != "user":
            continue
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = [p.get("text", "") for p in content if isinstance(p, dict) and p.get("type") == "text"]
            return "\n".join(parts) or "[contenido multimodal]"
    return ""


# ═══════════════════════════════════════════════════════════
# Endpoints
# ═══════════════════════════════════════════════════════════

@app.get("/health", response_model=HealthResponse)
async def health():
    """Diagnóstico completo del bridge y sus componentes."""
    set_start_time(_start_time)
    return diagnose(BRIDGE)


@app.get("/dashboard")
async def dashboard():
    """Dashboard web mínimo — HTML con estado en tiempo real."""
    from fastapi.responses import HTMLResponse
    from dashboard import DASHBOARD_HTML
    return HTMLResponse(content=DASHBOARD_HTML)


@app.get("/v1/models", response_model=ModelsListResponse)
async def list_models():
    return ModelsListResponse(data=AVAILABLE_MODELS)


@app.post("/v1/chat/completions")
async def chat_completions(req: ChatCompletionRequest, request: Request):
    # v2.0: Queue + Rate Limit + Shutdown
    if SHUTDOWN.shutting_down:
        code, body = error_response("SHUTTING_DOWN")
        return JSONResponse(content=body, status_code=code)

    # Streaming mode
    if req.stream:
        try:
            return await stream_chat(req, request, BRIDGE)
        except Exception as e:
            code, body = error_response("INTERNAL_ERROR", detail=str(e))
            return JSONResponse(content=body, status_code=code)

    # Non-streaming mode
    try:
        async with QUEUE:
            async with LIMITER:
                async with SHUTDOWN.track():
                    return await process_chat(req, request, BRIDGE)
    except QueueFullError:
        code, body = error_response("QUEUE_FULL", retry_after=5)
        return JSONResponse(content=body, status_code=code)
    except QueueTimeoutError:
        code, body = error_response("RATE_LIMITED", retry_after=10)
        return JSONResponse(content=body, status_code=code)
    except ShuttingDownError:
        code, body = error_response("SHUTTING_DOWN")
        return JSONResponse(content=body, status_code=code)


# ═══════════════════════════════════════════════════════════
# Agent endpoint (v3.1.0)
# ═══════════════════════════════════════════════════════════

from agent.agent import SimpleAgent

_agent = SimpleAgent()


@app.post("/v1/agent/chat")
async def agent_chat(req: ChatCompletionRequest, request: Request):
    """
    Chat con superpoderes: RAG + Skills + Memoria.
    El cliente puede pasar skill en el header X-Skill.
    """
    skill = request.headers.get("X-Skill", "default")
    use_memory = request.headers.get("X-Use-Memory", "true").lower() == "true"

    msgs = [m.model_dump() for m in req.messages]
    user_text = ""
    for m in reversed(msgs):
        if m.get("role") == "user":
            c = m.get("content", "")
            user_text = c if isinstance(c, str) else str(c)
            break

    if not user_text:
        code, body = error_response("BAD_REQUEST", detail="Sin mensaje del usuario")
        return JSONResponse(content=body, status_code=code)

    # Construir prompt enriquecido
    enriched = _agent.build_prompt(user_text, skill=skill, use_memory=use_memory)
    print(f"\n🎯 [agent][{skill}] {user_text[:120]}{'...' if len(user_text) > 120 else ''}")

    try:
        async with QUEUE:
            async with LIMITER:
                async with SHUTDOWN.track():
                    text, actual_model, gen_imgs, conv_id = await BRIDGE.send(
                        text=enriched, model=req.model,
                    )
    except Exception as e:
        code, body = error_response("INTERNAL_ERROR", detail=str(e))
        return JSONResponse(content=body, status_code=code)

    # Guardar en memoria
    conv_id = conv_id or f"agent-{uuid.uuid4().hex[:8]}"
    tags = [skill] if skill != "default" else []
    _agent.remember(conv_id, [
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": text},
    ], tags=tags)

    resp = JSONResponse(content=ChatCompletionResponse(
        id=f"chatcmpl-{uuid.uuid4().hex[:12]}",
        created=int(time.time()),
        model=actual_model,
        choices=[ChatChoice(index=0, message=ChatMessage(role="assistant", content=text), finish_reason="stop")],
        usage=UsageInfo(prompt_tokens=count_tokens(enriched), completion_tokens=count_tokens(text), total_tokens=count_tokens(enriched) + count_tokens(text)),
    ).model_dump())
    if conv_id:
        resp.headers["X-Conversation-ID"] = conv_id
    return resp


@app.get("/v1/agent/memory")
async def agent_memory():
    """Lista todas las conversaciones del agente."""
    return {"object": "list", "data": _agent.memory.list_all()}


@app.delete("/v1/agent/memory/{conv_id}")
async def agent_forget(conv_id: str):
    """Elimina una conversación de la memoria del agente."""
    _agent.forget(conv_id)
    return {"deleted": True, "conversation_id": conv_id}


@app.post("/v1/agent/reload")
async def agent_reload():
    """Recarga conocimiento y skills en caliente (hot-reload)."""
    _agent.reload_knowledge()
    return {"reloaded": True}


# ═══════════════════════════════════════════════════════════
# Entry
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="ChatGPT Web Bridge")
    p.add_argument("--port", type=int, default=9090)
    p.add_argument("--no-headless", action="store_true")
    args = p.parse_args()
    PORT = args.port
    HEADLESS = not args.no_headless
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="warning")


# ═══════════════════════════════════════════════════════════
# Entry
# ═══════════════════════════════════════════════════════════

PORT = 9090

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ChatGPT Web Bridge")
    parser.add_argument("--port", type=int, default=9090, help="Puerto del servidor (default: 9090)")
    parser.add_argument("--no-headless", action="store_true", help="Mostrar navegador (modo debug)")
    args = parser.parse_args()

    PORT = args.port
    HEADLESS = not args.no_headless

    print(f"\n🚀 Iniciando ChatGPT Web Bridge en http://localhost:{PORT}")
    print(f"   Modo: {'invisible' if HEADLESS else 'visible (debug)'}")
    print(f"   API Base URL: http://localhost:{PORT}/v1\n")

    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="warning")
