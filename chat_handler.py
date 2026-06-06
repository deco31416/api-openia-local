"""
Chat handler — Procesa requests de chat con toda la lógica de negocio.
Separado de server.py para mantener cada archivo <200 líneas.
"""

import uuid
import time

from fastapi import Request
from fastapi.responses import JSONResponse, StreamingResponse

from models import (
    ChatCompletionRequest, ChatCompletionResponse,
    ChatChoice, ChatMessage, UsageInfo,
)
from image_handler import ImageHandler
from token_counter import count_tokens
from session_store import get_store
from cost_tracker import get_tracker
from error_codes import error_response
from antiban import AntiBan
from sse_streamer import Streamer

# Anti-ban global (simula humano)
_antiban = AntiBan(human_mode=True, wpm=60)


def _last_user_text(messages: list) -> str:
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


async def process_chat(req: ChatCompletionRequest, request: Request, bridge):
    """Lógica completa de procesamiento de chat."""
    if bridge is None or not bridge.is_authenticated:
        code, body = error_response("AUTH_REQUIRED", detail="Bridge no autenticado en ChatGPT")
        return JSONResponse(content=body, status_code=code)
    msgs = [m.model_dump() for m in req.messages]
    prompt = _last_user_text(msgs)
    if not prompt and not ImageHandler.extract_base64_from_messages(msgs):
        code, body = error_response("BAD_REQUEST", detail="Sin contenido en el mensaje")
        return JSONResponse(content=body, status_code=code)

    images = ImageHandler.extract_base64_from_messages(msgs)
    conv_in = request.headers.get("X-Conversation-ID", "")
    tag = f"🖼️ +" if images else ""
    ctag = f" [chat:{conv_in[:8]}...]" if conv_in else ""
    print(f"\n📤 [{req.model}]{tag}{ctag} {prompt[:120]}{'...' if len(prompt) > 120 else ''}")

    # 🛡️ AntiBan: simular pausa humana entre requests
    await _antiban.inter_request_pause()

    # 🛡️ AntiBan: "pensar" antes de escribir
    await _antiban.thinking_pause()

    try:
        text, actual_model, gen_imgs, conv_id = await bridge.send(
            text=prompt, model=req.model, images=images or None,
            conversation_id=conv_in,
        )
    except Exception as e:
        print(f"❌ Error: {e}")
        code, body = error_response(
            "TIMEOUT" if "timeout" in str(e).lower() else "INTERNAL_ERROR",
            detail=str(e),
        )
        return JSONResponse(content=body, status_code=code)

    # 🛡️ AntiBan: "leer" la respuesta (simula humano)
    await _antiban.reading_pause()

    content: str | list[dict] = text
    if gen_imgs:
        parts: list[dict] = [{"type": "text", "text": text}]
        for url in gen_imgs:
            parts.append({"type": "image_url", "image_url": {"url": url}})
        content = parts  # type: ignore[assignment]

    imgs_tag = f" 🖼️ x{len(gen_imgs)}" if gen_imgs else ""
    conv_tag = f" [{conv_id[:8]}]" if conv_id else ""
    print(f"📥 [{actual_model}]{imgs_tag}{conv_tag}: {text[:120]}{'...' if len(text) > 120 else ''}")

    response_content = content if isinstance(content, str) else (
        content[0]["text"] if isinstance(content, list) and content else ""
    )

    prompt_tk = count_tokens(prompt)
    completion_tk = count_tokens(response_content)

    get_tracker().track(actual_model, prompt_tk, completion_tk)
    if conv_id:
        get_store().save(conv_id, actual_model, prompt, prompt_tk, completion_tk)

    payload = ChatCompletionResponse(
        id=f"chatcmpl-{uuid.uuid4().hex[:12]}",
        created=int(time.time()),
        model=actual_model,
        choices=[ChatChoice(index=0, message=ChatMessage(role="assistant", content=content), finish_reason="stop")],
        usage=UsageInfo(prompt_tokens=prompt_tk, completion_tokens=completion_tk, total_tokens=prompt_tk + completion_tk),
    )

    resp = JSONResponse(content=payload.model_dump())
    if conv_id:
        resp.headers["X-Conversation-ID"] = conv_id
        resp.headers["X-Conversation-URL"] = f"https://chatgpt.com/c/{conv_id}"
    return resp


async def stream_chat(req: ChatCompletionRequest, request: Request, bridge):
    """
    Versión streaming: emite tokens incrementalmente via SSE.
    Divide la respuesta en chunks con tiktoken y delay artificial.
    """
    from sse_streamer import Streamer

    msgs = [m.model_dump() for m in req.messages]
    prompt = _last_user_text(msgs)
    images = ImageHandler.extract_base64_from_messages(msgs)
    conv_in = request.headers.get("X-Conversation-ID", "")

    await _antiban.inter_request_pause()
    await _antiban.thinking_pause()

    try:
        text, actual_model, gen_imgs, conv_id = await bridge.send(
            text=prompt, model=req.model, images=images or None,
            conversation_id=conv_in,
        )
    except Exception as e:
        # Error en streaming: enviar como SSE error y cerrar
        async def error_stream():
            err = json.dumps({"error": {"code": "STREAM_ERROR", "message": str(e)}})
            yield f"data: {err}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")

    # Track tokens
    prompt_tk = count_tokens(prompt)
    completion_tk = count_tokens(text)
    get_tracker().track(actual_model, prompt_tk, completion_tk)
    if conv_id:
        get_store().save(conv_id, actual_model, prompt, prompt_tk, completion_tk)

    streamer = Streamer(delay_ms=30, chunk_tokens=1)
    return StreamingResponse(
        streamer.stream(text, actual_model),
        media_type="text/event-stream",
        headers={
            "X-Conversation-ID": conv_id or "",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
