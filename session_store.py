"""
Session Store — Persiste metadatos de conversaciones en JSON local.
Sobrevive a reinicios del bridge, apagones y reinicios del navegador.
"""

import json
import time
import os
from pathlib import Path
from typing import Optional


class SessionStore:
    """
    Guarda y recupera conversaciones de ChatGPT en un archivo JSON local.

    Estructura:
    {
      "a1b2c3d4...": {
        "conversation_id": "a1b2c3d4...",
        "model": "gpt-4o",
        "url": "https://chatgpt.com/c/a1b2c3d4...",
        "created_at": 1715367049,
        "last_used_at": 1715367100,
        "summary": "Primeros 100 chars del prompt inicial"
      }
    }
    """

    def __init__(self, filepath: str = "conversations.json"):
        self._path = Path(filepath)
        self._data: dict = {}
        self._load()

    # ── CRUD ─────────────────────────────────────────────

    def save(self, conversation_id: str, model: str, prompt: str,
             prompt_tokens: int = 0, completion_tokens: int = 0):
        """Guarda o actualiza una conversación con conteo de tokens."""
        now = int(time.time())
        entry = {
            "conversation_id": conversation_id,
            "model": model,
            "url": f"https://chatgpt.com/c/{conversation_id}",
            "last_used_at": now,
            "summary": prompt[:80].replace("\n", " "),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        }
        if conversation_id in self._data:
            # Acumular tokens del chat existente
            prev = self._data[conversation_id]
            entry["prompt_tokens"] = prev.get("prompt_tokens", 0) + prompt_tokens
            entry["completion_tokens"] = prev.get("completion_tokens", 0) + completion_tokens
            entry["total_tokens"] = entry["prompt_tokens"] + entry["completion_tokens"]
            entry["created_at"] = prev.get("created_at", now)
        else:
            entry["created_at"] = now

        self._data[conversation_id] = entry
        self._flush()

    def get(self, conversation_id: str) -> Optional[dict]:
        return self._data.get(conversation_id)

    def list_all(self) -> list[dict]:
        """Devuelve conversaciones ordenadas por last_used_at descendente."""
        return sorted(
            self._data.values(), key=lambda x: x.get("last_used_at", 0), reverse=True
        )

    def delete(self, conversation_id: str):
        if conversation_id in self._data:
            del self._data[conversation_id]
            self._flush()

    # ── Internals ────────────────────────────────────────

    def _load(self):
        if self._path.exists():
            try:
                self._data = json.loads(self._path.read_text("utf-8"))
            except (json.JSONDecodeError, OSError):
                self._data = {}

    def _flush(self):
        self._path.write_text(json.dumps(self._data, indent=2, ensure_ascii=False), "utf-8")


# ── Singleton ────────────────────────────────────────────

_store: Optional[SessionStore] = None


def get_store() -> SessionStore:
    global _store
    if _store is None:
        _store = SessionStore()
    return _store
