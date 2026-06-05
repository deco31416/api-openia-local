"""
ChatGPT Web Bridge — Servidor API compatible con OpenAI.

Endpoints:
    GET  /health                 → Estado del bridge
    GET  /v1/models              → Modelos disponibles
    POST /v1/chat/completions    → Chat (texto + imágenes, OpenAI SDK compatible)

Uso:
    python server.py --port 9090           # visible (login)
    python server.py --port 9090 --no-headless  # invisible
"""

import sys
import time
import uuid
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import uvicorn

from models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatChoice,
    ChatMessage,
    UsageInfo,
    ModelInfo,
    ModelsListResponse,
    HealthResponse,
)
from chatgpt_bridge import ChatGPTBridge
from image_handler import ImageHandler
from token_counter import count_tokens
from session_store import get_store
from cost_tracker import get_tracker


# ═══════════════════════════════════════════════════════════
# Config
# ═══════════════════════════════════════════════════════════

BRIDGE: ChatGPTBridge = None  # type: ignore
HEADLESS = True
PORT = 9090

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

@asynccontextmanager
async def lifespan(app: FastAPI):
    global BRIDGE
    banner()
    BRIDGE = await ChatGPTBridge(headless=HEADLESS).start()
    if not BRIDGE.is_authenticated:
        await _wait_for_login()
    print("\n✅ Bridge listo! API activa.\n")
    yield
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


app = FastAPI(title="ChatGPT Web Bridge", version="1.1.0", lifespan=lifespan)


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
    return HealthResponse(
        status="ok",
        authenticated=BRIDGE.is_authenticated if BRIDGE else False,
    )


@app.get("/v1/models", response_model=ModelsListResponse)
async def list_models():
    return ModelsListResponse(data=AVAILABLE_MODELS)


@app.post("/v1/chat/completions")
async def chat_completions(req: ChatCompletionRequest, request: Request):
    if BRIDGE is None:
        raise HTTPException(503, "Bridge no inicializado")

    msgs = [m.model_dump() for m in req.messages]
    prompt = _last_user_text(msgs)
    if not prompt and not ImageHandler.extract_base64_from_messages(msgs):
        raise HTTPException(400, "Sin contenido en el mensaje del usuario")

    images = ImageHandler.extract_base64_from_messages(msgs)
    conv_in = request.headers.get("X-Conversation-ID", "")
    tag = f"🖼️ +" if images else ""
    ctag = f" [chat:{conv_in[:8]}...]" if conv_in else ""
    print(f"\n📤 [{req.model}]{tag}{ctag} {prompt[:120]}{'...' if len(prompt) > 120 else ''}")

    try:
        text, actual_model, gen_imgs, conv_id = await BRIDGE.send(
            text=prompt, model=req.model, images=images or None,
            conversation_id=conv_in,
        )
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(500, f"Error en ChatGPT Web: {str(e)}")

    # Imágenes generadas → contenido multimodal
    content: str | list[dict] = text
    if gen_imgs:
        content_parts: list[dict] = [{"type": "text", "text": text}]
        for url in gen_imgs:
            content_parts.append({"type": "image_url", "image_url": {"url": url}})
        content = content_parts  # type: ignore[assignment]

    imgs_tag = f" 🖼️ x{len(gen_imgs)}" if gen_imgs else ""
    conv_tag = f" [{conv_id[:8]}]" if conv_id else ""
    print(f"📥 [{actual_model}]{imgs_tag}{conv_tag}: {text[:120]}{'...' if len(text) > 120 else ''}")

    response_content = content if isinstance(content, str) else (
        content[0]["text"] if isinstance(content, list) and content else ""
    )

    prompt_tk = count_tokens(prompt)
    completion_tk = count_tokens(response_content)

    # Registrar en el cost tracker
    tracker = get_tracker()
    tracker.track(actual_model, prompt_tk, completion_tk)

    payload = ChatCompletionResponse(
        id=f"chatcmpl-{uuid.uuid4().hex[:12]}",
        created=int(time.time()),
        model=actual_model,
        choices=[
            ChatChoice(
                index=0,
                message=ChatMessage(role="assistant", content=content),
                finish_reason="stop",
            )
        ],
        usage=UsageInfo(
            prompt_tokens=prompt_tk,
            completion_tokens=completion_tk,
            total_tokens=prompt_tk + completion_tk,
        ),
    )

    resp = JSONResponse(content=payload.model_dump())
    if conv_id:
        resp.headers["X-Conversation-ID"] = conv_id
        resp.headers["X-Conversation-URL"] = f"https://chatgpt.com/c/{conv_id}"
    return resp


# ═══════════════════════════════════════════════════════════
# Conversaciones (session store)
# ═══════════════════════════════════════════════════════════

@app.get("/v1/conversations")
async def list_conversations():
    """Lista todas las conversaciones guardadas (sobrevive a reinicios)."""
    store = get_store()
    return {"object": "list", "data": store.list_all()}


@app.delete("/v1/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Elimina una conversación del store."""
    store = get_store()
    entry = store.get(conversation_id)
    if not entry:
        raise HTTPException(404, f"Conversación '{conversation_id}' no encontrada")
    store.delete(conversation_id)
    return {"deleted": True, "conversation_id": conversation_id}


@app.get("/v1/usage")
async def usage():
    """Resumen de tokens acumulados y costo estimado en USD."""
    return get_tracker().summary()


@app.delete("/v1/usage")
async def reset_usage():
    """Reinicia el contador de tokens y costos."""
    get_tracker().reset()
    return {"reset": True}

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
