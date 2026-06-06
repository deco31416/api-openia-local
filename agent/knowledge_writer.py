"""
Knowledge Writer — Genera archivos .md en skills/ y knowledge/
de forma manual (comando !save) o automática (detección de patrones).
"""

import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional


class KnowledgeWriter:
    """
    Escribe archivos .md en las carpetas del agente.
    Soporta generación manual y sugerencias automáticas.

    Uso:
        kw = KnowledgeWriter("agent/skills", "agent/knowledge")
        kw.save_skill("react-patterns", "## Patrones React\n...")
        suggestion = kw.detect_pattern(recent_messages)
    """

    def __init__(self, skills_dir: str = "agent/skills", knowledge_dir: str = "agent/knowledge"):
        self._skills = Path(skills_dir)
        self._knowledge = Path(knowledge_dir)
        self._skills.mkdir(parents=True, exist_ok=True)
        self._knowledge.mkdir(parents=True, exist_ok=True)
        self._pattern_counts: dict[str, int] = {}

    # ── Escritura manual ─────────────────────────────────

    def save_skill(self, name: str, content: str) -> Path:
        """Guarda un skill como .md. name sin extensión, sin espacios raros."""
        safe_name = re.sub(r"[^a-zA-Z0-9_-]", "-", name.lower()).strip("-") or "untitled"
        path = self._skills / f"{safe_name}.md"
        path.write_text(content.strip() + "\n", encoding="utf-8")
        print(f"[Writer] 💾 Skill guardado: {path}")
        return path

    def save_knowledge(self, name: str, content: str) -> Path:
        """Guarda conocimiento como .md."""
        safe_name = re.sub(r"[^a-zA-Z0-9_-]", "-", name.lower()).strip("-") or "nota"
        # Añadir timestamp si ya existe
        path = self._knowledge / f"{safe_name}.md"
        if path.exists():
            safe_name = f"{safe_name}-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
            path = self._knowledge / f"{safe_name}.md"
        header = f"# {name}\n\n_Generado: {datetime.now(timezone.utc).isoformat()}_\n\n"
        path.write_text(header + content.strip() + "\n", encoding="utf-8")
        print(f"[Writer] 📝 Conocimiento guardado: {path}")
        return path

    def save_summary(self, conversation_id: str, content: str) -> Path:
        """Guarda un resumen en memory/summaries/."""
        summaries_dir = Path("agent/memory/summaries")
        summaries_dir.mkdir(parents=True, exist_ok=True)
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        path = summaries_dir / f"{date_str}-{conversation_id[:8]}.md"
        header = f"# Resumen de conversación {conversation_id[:8]}\n\n_Fecha: {datetime.now(timezone.utc).isoformat()}_\n\n"
        path.write_text(header + content.strip() + "\n", encoding="utf-8")
        print(f"[Writer] 📋 Resumen guardado: {path}")
        return path

    # ── Detección de patrones (auto-sugerencia) ──────────

    def detect_pattern(
        self,
        recent_messages: list[dict],
        min_occurrences: int = 3,
    ) -> Optional[dict]:
        """
        Detecta si hay un patrón recurrente que merezca guardarse.
        Busca URLs/valores que aparecen múltiples veces en correcciones del usuario.
        """
        topics: dict[str, list[str]] = {}

        for msg in recent_messages[-20:]:
            text = msg.get("content", "")
            if not isinstance(text, str) or msg.get("role") != "user":
                continue

            # Detectar URLs mencionadas en contexto correctivo
            import re
            urls = re.findall(r'https?://[^\s,.]+', text)
            # Detectar frases como "la URL es X", "X es correcto"
            phrases = re.findall(
                r'(?:la|el)\s+\w+(?:\s+(?:correct[oa]|URL|API|endpoint))?\s+(?:es|son)\s+(\S+)',
                text, re.IGNORECASE
            )

            for url in urls:
                key = f"correction:url"
                topics.setdefault(key, []).append(url)

            for phrase in phrases:
                key = f"correction:value"
                topics.setdefault(key, []).append(phrase)

        for key, values in topics.items():
            if len(values) >= min_occurrences:
                _, topic = key.split(":", 1)
                return {
                    "type": "correction",
                    "topic": topic,
                    "value": values[-1],
                    "count": len(values),
                }

        return None

    def build_suggestion(self, trigger: dict) -> str:
        """Construye un mensaje de sugerencia para el usuario."""
        if trigger["type"] == "correction":
            return (
                f"He notado que has corregido {trigger['count']} veces "
                f"algo sobre '{trigger['topic']}'. Último valor: {trigger['value']}.\n"
                f"¿Quieres que guarde una nota de conocimiento con este dato? "
                f"Responde 'sí' o '!save knowledge {trigger['topic']}'."
            )
        return ""
