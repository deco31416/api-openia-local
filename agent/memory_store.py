"""
Memory Store — Persistencia de conversaciones en archivos .json.
Índice rápido, búsqueda por tags/palabras clave, auto-resumen.
"""

import json
import os
import re
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional


class MemoryStore:
    """
    Almacena conversaciones en agent/memory/conversations/*.json.
    Mantiene un índice en agent/memory/summary.json.

    Uso:
        mem = MemoryStore("agent/memory")
        mem.save("conv-001", messages, tags=["cocina"])
        mem.save("conv-001", [{"role":"assistant","content":"..."}])  # append
        history = mem.search("paella")  # busca en conversaciones pasadas
    """

    def __init__(self, memory_dir: str = "agent/memory"):
        self._dir = Path(memory_dir)
        self._conv_dir = self._dir / "conversations"
        self._summary_path = self._dir / "summary.json"
        self._summary: dict = {}
        self._ensure_dirs()
        self._load_summary()

    # ── CRUD ─────────────────────────────────────────────

    def save(self, conv_id: str, messages: list[dict], tags: list[str] | None = None,
             summary: str = "", pinned: bool = False):
        """Guarda o actualiza una conversación."""
        now = datetime.now(timezone.utc).isoformat()

        # Si el archivo ya existe, hacer append
        existing = self._load_conv(conv_id)
        if existing:
            existing["messages"].extend(messages)
            existing["tags"] = list(set(existing.get("tags", []) + (tags or [])))
            existing["pinned"] = pinned or existing.get("pinned", False)
            if summary:
                existing["summary"] = summary
        else:
            existing = {
                "id": conv_id,
                "timestamp": now,
                "summary": summary or self._auto_summary(messages),
                "messages": messages,
                "tags": tags or [],
                "pinned": pinned,
            }

        self._write_conv(conv_id, existing)
        self._update_summary(conv_id, existing)

    def load(self, conv_id: str) -> Optional[dict]:
        """Carga una conversación por ID."""
        return self._load_conv(conv_id)

    def delete(self, conv_id: str):
        """Elimina una conversación."""
        filepath = self._conv_dir / f"{conv_id}.json"
        if filepath.exists():
            filepath.unlink()
        if conv_id in self._summary:
            del self._summary[conv_id]
            self._write_summary()

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        """
        Busca conversaciones relevantes por keywords en summary, tags, y mensajes.
        Retorna mensajes relevantes formateados como string de contexto.
        """
        terms = query.lower().split()
        results: list[tuple[str, float]] = []

        for conv_id, info in self._summary.items():
            score = 0.0
            searchable = f"{info.get('summary','')} {' '.join(info.get('tags',[]))}"
            searchable_lower = searchable.lower()
            for term in terms:
                if term in searchable_lower:
                    score += 1.0
                # Penalizar matches parciales
                elif any(term[:-1] in searchable_lower for _ in [1] if len(term) > 2):
                    score += 0.3
            if score > 0:
                results.append((conv_id, score))

        results.sort(key=lambda x: x[1], reverse=True)
        contexts: list[dict] = []
        for conv_id, _ in results[:top_k]:
            conv = self._load_conv(conv_id)
            if conv:
                contexts.append(conv)
        return contexts

    def list_all(self) -> list[dict]:
        """Lista todas las conversaciones (desde el índice)."""
        return sorted(
            list(self._summary.values()),
            key=lambda x: x.get("timestamp", ""),
            reverse=True,
        )

    # ── Internals ────────────────────────────────────────

    def _ensure_dirs(self):
        self._dir.mkdir(parents=True, exist_ok=True)
        self._conv_dir.mkdir(parents=True, exist_ok=True)

    def _load_conv(self, conv_id: str) -> Optional[dict]:
        filepath = self._conv_dir / f"{conv_id}.json"
        if filepath.exists():
            try:
                return json.loads(filepath.read_text("utf-8"))
            except (json.JSONDecodeError, OSError):
                return None
        return None

    def _write_conv(self, conv_id: str, data: dict):
        filepath = self._conv_dir / f"{conv_id}.json"
        filepath.write_text(json.dumps(data, indent=2, ensure_ascii=False), "utf-8")

    def _load_summary(self):
        if self._summary_path.exists():
            self._summary = json.loads(self._summary_path.read_text("utf-8"))

    def _write_summary(self):
        self._summary_path.write_text(json.dumps(self._summary, indent=2, ensure_ascii=False), "utf-8")

    def _update_summary(self, conv_id: str, data: dict):
        self._summary[conv_id] = {
            "id": conv_id,
            "timestamp": data.get("timestamp", ""),
            "summary": data.get("summary", ""),
            "tags": data.get("tags", []),
            "pinned": data.get("pinned", False),
            "message_count": len(data.get("messages", [])),
        }
        self._write_summary()

    @staticmethod
    def _auto_summary(messages: list[dict], max_len: int = 80) -> str:
        """Genera un resumen automático desde el primer mensaje del usuario."""
        for msg in messages:
            if msg.get("role") == "user":
                text = msg.get("content", "")
                if isinstance(text, str):
                    return text[:max_len].replace("\n", " ").strip()
        return "Conversación sin título"
