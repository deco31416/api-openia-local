"""
Rutas adicionales: conversaciones y uso.
Separadas de server.py para mantener cada archivo <200 líneas.
"""

from fastapi import APIRouter, HTTPException
from session_store import get_store
from cost_tracker import get_tracker, get_price

router = APIRouter(prefix="/v1", tags=["conversations", "usage"])


# ═══════════════════════════════════════════════════════════
# Conversaciones
# ═══════════════════════════════════════════════════════════

@router.get("/conversations")
async def list_conversations():
    """Lista todas las conversaciones guardadas con sus tokens."""
    store = get_store()
    return {"object": "list", "data": store.list_all()}


@router.get("/conversations/{conversation_id}/usage")
async def conversation_usage(conversation_id: str):
    """Tokens y costo estimado para una conversación específica."""
    store = get_store()
    entry = store.get(conversation_id)
    if not entry:
        raise HTTPException(404, f"Conversación '{conversation_id}' no encontrada")
    pt = entry.get("prompt_tokens", 0)
    ct = entry.get("completion_tokens", 0)
    model = entry.get("model", "gpt-4o")
    ci, co, total = get_price(model, pt, ct)
    return {
        "conversation_id": conversation_id,
        "model": model,
        "url": entry.get("url"),
        "prompt_tokens": pt,
        "completion_tokens": ct,
        "total_tokens": pt + ct,
        "cost_input_usd": ci,
        "cost_output_usd": co,
        "cost_total_usd": total,
    }


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Elimina una conversación del store."""
    store = get_store()
    entry = store.get(conversation_id)
    if not entry:
        raise HTTPException(404, f"Conversación '{conversation_id}' no encontrada")
    store.delete(conversation_id)
    return {"deleted": True, "conversation_id": conversation_id}


# ═══════════════════════════════════════════════════════════
# Uso / Costos
# ═══════════════════════════════════════════════════════════

@router.get("/usage")
async def usage():
    """Resumen global de tokens acumulados y costo estimado en USD."""
    return get_tracker().summary()


@router.delete("/usage")
async def reset_usage():
    """Reinicia el contador global de tokens y costos."""
    get_tracker().reset()
    return {"reset": True}
