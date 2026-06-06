"""
Agent endpoints — separados de server.py para mantener <200 líneas.
"""

import uuid
import time
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from models import (
    ChatCompletionRequest, ChatCompletionResponse,
    ChatChoice, ChatMessage, UsageInfo,
)
from token_counter import count_tokens
from error_codes import error_response

router = APIRouter(prefix="/v1/agent", tags=["agent"])


def _get_agent():
    """Lazy import del agente y el bridge desde server."""
    import server
    return server._agent, server.BRIDGE, server.QUEUE, server.LIMITER, server.SHUTDOWN


@router.post("/chat")
async def agent_chat(req: ChatCompletionRequest, request: Request):
    agent, bridge, queue, limiter, shutdown = _get_agent()
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

    enriched = agent.build_prompt(user_text, skill=skill, use_memory=use_memory)
    print(f"\n🎯 [agent][{skill}] {user_text[:120]}{'...' if len(user_text) > 120 else ''}")

    try:
        async with queue:
            async with limiter:
                async with shutdown.track():
                    text, actual_model, gen_imgs, conv_id = await bridge.send(
                        text=enriched, model=req.model,
                    )
    except Exception as e:
        code, body = error_response("INTERNAL_ERROR", detail=str(e))
        return JSONResponse(content=body, status_code=code)

    conv_id = conv_id or f"agent-{uuid.uuid4().hex[:8]}"
    tags = [skill] if skill != "default" else []
    agent.remember(conv_id, [
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": text},
    ], tags=tags)

    extra_info: dict = {}
    if user_text.strip().lower().startswith("!save"):
        extra_info = _handle_save_command(agent, user_text, text)

    suggestion = agent.detect_learning([
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": text},
    ])
    if suggestion and not extra_info:
        extra_info["suggestion"] = suggestion

    resp = JSONResponse(content=ChatCompletionResponse(
        id=f"chatcmpl-{uuid.uuid4().hex[:12]}",
        created=int(time.time()),
        model=actual_model,
        choices=[ChatChoice(index=0, message=ChatMessage(
            role="assistant",
            content=text + _format_extra(extra_info)
        ), finish_reason="stop")],
        usage=UsageInfo(
            prompt_tokens=count_tokens(enriched),
            completion_tokens=count_tokens(text),
            total_tokens=count_tokens(enriched) + count_tokens(text),
        ),
    ).model_dump())
    if conv_id:
        resp.headers["X-Conversation-ID"] = conv_id
    return resp


@router.get("/memory")
async def agent_memory():
    agent, _, _, _, _ = _get_agent()
    return {"object": "list", "data": agent.memory.list_all()}


@router.delete("/memory/{conv_id}")
async def agent_forget(conv_id: str):
    agent, _, _, _, _ = _get_agent()
    agent.forget(conv_id)
    return {"deleted": True, "conversation_id": conv_id}


@router.get("/memory/{conv_id}")
async def agent_recall(conv_id: str):
    """Recupera una conversación específica por ID."""
    agent, _, _, _, _ = _get_agent()
    conv = agent.recall(conv_id)
    if not conv:
        return JSONResponse(status_code=404, content={"error": {"code": "NOT_FOUND", "message": f"Conversación '{conv_id}' no encontrada"}})
    return conv


@router.post("/reload")
async def agent_reload():
    agent, _, _, _, _ = _get_agent()
    agent.rag.reload()
    return {"reloaded": True}


def _handle_save_command(agent, user_text: str, response_text: str) -> dict:
    info: dict = {}
    text_lower = user_text.strip().lower()
    try:
        if text_lower.startswith("!save skill "):
            name = user_text.strip()[12:].strip().split("\n")[0]
            path = agent.save_skill(name, response_text)
            info["saved_skill"] = str(path)
        elif text_lower.startswith("!save knowledge "):
            name = user_text.strip()[17:].strip().split("\n")[0]
            path = agent.save_knowledge(name, response_text)
            info["saved_knowledge"] = str(path)
        elif text_lower.startswith("!save summary"):
            conv_id = f"summary-{uuid.uuid4().hex[:8]}"
            path = agent.save_summary(conv_id, response_text)
            info["saved_summary"] = str(path)
    except Exception as e:
        info["save_error"] = str(e)
    return info


def _format_extra(extra: dict) -> str:
    parts = []
    if extra.get("saved_skill"):
        parts.append(f"\n\n✅ Skill guardado: `{extra['saved_skill']}`")
    if extra.get("saved_knowledge"):
        parts.append(f"\n\n📝 Conocimiento guardado: `{extra['saved_knowledge']}`")
    if extra.get("saved_summary"):
        parts.append(f"\n\n📋 Resumen guardado: `{extra['saved_summary']}`")
    if extra.get("suggestion"):
        parts.append(f"\n\n💡 {extra['suggestion']}")
    if extra.get("save_error"):
        parts.append(f"\n\n⚠️ Error: {extra['save_error']}")
    return "".join(parts)
