"""
ChatGPT Web Bridge — Servidor API compatible con OpenAI.

Uso:
    python server.py --port 9090           # visible
    python server.py --port 9090 --no-headless  # invisible
"""

import sys
import time
import uuid
import os
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
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
from agent_handler import router as agent_router

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
HOST = "127.0.0.1"
API_KEY = os.getenv("BRIDGE_API_KEY", "")
QUEUE: RequestQueue = RequestQueue(max_concurrent=1, max_queue=10)
LIMITER: RateLimiter = RateLimiter(rpm=10, burst=3)
SHUTDOWN: GracefulShutdown = GracefulShutdown(timeout=30.0)
WATCHDOG: Watchdog = None  # type: ignore
SESSION_RECOVERY: SessionRecovery = None  # type: ignore

AVAILABLE_MODELS = [
    ModelInfo(id="o3-5.5-instant", created=1750000000, owned_by="chatgpt-web"),
    ModelInfo(id="o3-5.5-thinking", created=1750000001, owned_by="chatgpt-web"),
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

    # 🛡️ Session Recovery: restaurar cookies guardadas
    if SESSION_RECOVERY:
        restored = await SESSION_RECOVERY.restore()
        if restored:
            valid = await SESSION_RECOVERY.ensure_valid(page, timeout=5)
            print(f"[Session] {'✅' if valid else '⚠️'} Sesión {'válida' if valid else 'expirada — login manual requerido'}")

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


app = FastAPI(title="ChatGPT Web Bridge", version="3.3.0", lifespan=lifespan)
app.include_router(v1_router)
app.include_router(agent_router, prefix="/v1")


# ═══════════════════════════════════════════════════════════
# Middleware: API Key (simple, sin castillos)
# ═══════════════════════════════════════════════════════════

SKIP_AUTH_PATHS = {"/health", "/docs", "/openapi.json", "/dashboard", "/favicon.ico"}


@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    """Middleware opcional: si BRIDGE_API_KEY está definida, la exige."""
    if API_KEY and request.url.path not in SKIP_AUTH_PATHS:
        key = request.headers.get("X-API-Key", "")
        if key != API_KEY:
            return JSONResponse(status_code=401, content={
                "error": {"code": "UNAUTHORIZED", "message": "X-API-Key inválida o ausente"}
            })
    return await call_next(request)


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
# Agent (v3.1.0 — movido a agent_handler.py)
# ═══════════════════════════════════════════════════════════

from agent.agent import SimpleAgent
from agent_handler import router as agent_router_app

_agent = SimpleAgent()
app.include_router(agent_router_app, prefix="/v1")


# ═══════════════════════════════════════════════════════════
# Entry
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="ChatGPT Web Bridge")
    p.add_argument("--port", type=int, default=9090, help="Puerto (default: 9090)")
    p.add_argument("--host", type=str, default="127.0.0.1", help="Host (default: 127.0.0.1)")
    p.add_argument("--no-headless", action="store_true", help="Navegador visible")
    p.add_argument("--api-key", type=str, default="", help="API key requerida en X-API-Key header")
    args = p.parse_args()
    PORT = args.port
    HOST = args.host
    HEADLESS = not args.no_headless
    if args.api_key:
        API_KEY = args.api_key
    if not API_KEY:
        API_KEY = os.getenv("BRIDGE_API_KEY", "")
    secure = "🔒" if API_KEY else "🔓"
    print(f"  Host: {HOST}:{PORT} {secure}")
    uvicorn.run(app, host=HOST, port=PORT, log_level="warning")


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
