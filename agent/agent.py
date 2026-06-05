"""
SimpleAgent — Orquestador que une RAG + Skills + Memoria + Bridge + Writer.
Menos de 200 líneas, cero dependencias pesadas.
"""

from pathlib import Path
from typing import Optional

from agent.rag import RAGEngine
from agent.memory_store import MemoryStore
from agent.knowledge_writer import KnowledgeWriter


class SimpleAgent:
    """
    Agente que enriquece prompts Y genera conocimiento automáticamente.

    Uso:
        agent = SimpleAgent()
        enriched = agent.build_prompt("¿Cómo hago paella?", skill="default")
        agent.save_skill("code-review-ts", "## TypeScript patterns...")
        suggestion = agent.detect_learning(recent_msgs)  # auto-sugerencia
    """

    def __init__(
        self,
        knowledge_dir: str = "agent/knowledge",
        skills_dir: str = "agent/skills",
        memory_dir: str = "agent/memory",
    ):
        self.rag = RAGEngine(knowledge_dir)
        self.skills = self._load_skills(skills_dir)
        self.memory = MemoryStore(memory_dir)
        self.writer = KnowledgeWriter(skills_dir, knowledge_dir)
        self._skills_dir = skills_dir
        self._knowledge_dir = knowledge_dir

    # ── Prompt Building ──────────────────────────────────

    def build_prompt(self, user_message: str, skill: str = "default",
                     use_memory: bool = True, max_context_chars: int = 2000) -> str:
        parts: list[str] = []
        system = self.skills.get(skill, "")
        if system:
            parts.append(f"[SYSTEM]\n{system}")
        fragments = self.rag.search(user_message, top_k=3)
        if fragments:
            ctx = "\n---\n".join(fragments)
            if len(ctx) > max_context_chars:
                ctx = ctx[:max_context_chars] + "\n... (truncado)"
            parts.append(f"[CONTEXT]\n{ctx}")
        if use_memory:
            history = self.memory.search(user_message, top_k=2)
            if history:
                htexts = []
                for conv in history:
                    for msg in conv.get("messages", [])[-4:]:
                        role = msg.get("role", "user")
                        content = msg.get("content", "")
                        if isinstance(content, str) and content.strip():
                            htexts.append(f"[{role}] {content[:200]}")
                if htexts:
                    parts.append(f"[HISTORY]\n" + "\n".join(htexts))
        parts.append(f"[USER]\n{user_message}")
        return "\n\n".join(parts)

    # ── Memory ───────────────────────────────────────────

    def remember(self, conv_id: str, messages: list[dict], tags: list[str] | None = None):
        self.memory.save(conv_id, messages, tags=tags)

    def recall(self, conv_id: str) -> Optional[dict]:
        return self.memory.load(conv_id)

    def forget(self, conv_id: str):
        self.memory.delete(conv_id)

    # ── Knowledge Writing ────────────────────────────────

    def save_skill(self, name: str, content: str) -> Path:
        """Guarda un nuevo skill .md y lo recarga en caliente."""
        path = self.writer.save_skill(name, content)
        self.skills = self._load_skills(self._skills_dir)  # reload
        return path

    def save_knowledge(self, name: str, content: str) -> Path:
        """Guarda conocimiento .md y recarga RAG."""
        path = self.writer.save_knowledge(name, content)
        self.rag.reload()
        return path

    def save_summary(self, conv_id: str, content: str) -> Path:
        """Guarda resumen de conversación."""
        return self.writer.save_summary(conv_id, content)

    def detect_learning(self, recent_messages: list[dict]) -> Optional[str]:
        """
        Detecta patrones de aprendizaje y devuelve sugerencia o None.
        El caller decide si mostrar la sugerencia al usuario.
        """
        trigger = self.writer.detect_pattern(recent_messages)
        if trigger:
            return self.writer.build_suggestion(trigger)
        return None

    # ── Internals ────────────────────────────────────────

    @staticmethod
    def _load_skills(skills_dir: str) -> dict[str, str]:
        skills: dict[str, str] = {}
        path = Path(skills_dir)
        path.mkdir(parents=True, exist_ok=True)
        for md_file in path.glob("*.md"):
            name = md_file.stem
            skills[name] = md_file.read_text("utf-8")
        print(f"[Agent] 🎯 {len(skills)} skills cargadas de {path}")
        return skills
