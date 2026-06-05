"""
SimpleAgent — Orquestador que une RAG + Skills + Memoria + Bridge.
Menos de 200 líneas, cero dependencias pesadas.
"""

from pathlib import Path
from typing import Optional

from agent.rag import RAGEngine
from agent.memory_store import MemoryStore


class SimpleAgent:
    """
    Agente que enriquece prompts con conocimiento, skills y memoria.

    Uso:
        agent = SimpleAgent()
        enriched_prompt = agent.build_prompt("¿Cómo hago paella?", skill="default")
        response = await bridge.send(enriched_prompt, model="gpt-4o")
        agent.remember("conv-001", [{"role":"user","content":"..."},
                                    {"role":"assistant","content":response}])
    """

    def __init__(
        self,
        knowledge_dir: str = "agent/knowledge",
        skills_dir: str = "agent/skills",
        memory_dir: str = "agent/memory",
        use_embeddings: bool = False,
    ):
        self.knowledge = RAGEngine(knowledge_dir)
        self.skills = self._load_skills(skills_dir)
        self.memory = MemoryStore(memory_dir)

        if use_embeddings:
            ok = self.knowledge.enable_embeddings()
            print(f"[Agent] 🧠 Embeddings: {'OK' if ok else 'fallback a keywords'}")

    # ── Prompt Building ──────────────────────────────────

    def build_prompt(
        self,
        user_message: str,
        skill: str = "default",
        use_memory: bool = True,
        max_context_chars: int = 2000,
    ) -> str:
        """
        Construye un prompt enriquecido con:
        1. System prompt de la skill
        2. Fragmentos relevantes de knowledge/
        3. Contexto de conversaciones pasadas (memory)
        4. El mensaje del usuario
        """
        parts: list[str] = []

        # 1. Skill (system prompt)
        system = self.skills.get(skill, "")
        if system:
            parts.append(f"[SYSTEM]\n{system}")

        # 2. Conocimiento (RAG)
        fragments = self.knowledge.search(user_message, top_k=3)
        if fragments:
            context = "\n---\n".join(fragments)
            if len(context) > max_context_chars:
                context = context[:max_context_chars] + "\n... (truncado)"
            parts.append(f"[CONTEXT]\n{context}")

        # 3. Memoria (historial relevante)
        if use_memory:
            history = self.memory.search(user_message, top_k=2)
            if history:
                hist_texts: list[str] = []
                for conv in history:
                    msgs = conv.get("messages", [])[-4:]  # últimos 4 mensajes
                    for msg in msgs:
                        role = msg.get("role", "user")
                        content = msg.get("content", "")
                        if isinstance(content, str) and content.strip():
                            hist_texts.append(f"[{role}] {content[:200]}")
                if hist_texts:
                    parts.append(f"[HISTORY]\n" + "\n".join(hist_texts))

        # 4. Mensaje del usuario
        parts.append(f"[USER]\n{user_message}")

        return "\n\n".join(parts)

    # ── Memory Management ────────────────────────────────

    def remember(self, conv_id: str, messages: list[dict], tags: list[str] | None = None):
        """Guarda una conversación en memoria persistente."""
        self.memory.save(conv_id, messages, tags=tags)

    def recall(self, conv_id: str) -> Optional[dict]:
        """Recupera una conversación por ID."""
        return self.memory.load(conv_id)

    def forget(self, conv_id: str):
        """Elimina una conversación de la memoria."""
        self.memory.delete(conv_id)

    def search_memory(self, query: str) -> list[dict]:
        """Busca conversaciones pasadas relevantes."""
        return self.memory.search(query)

    # ── Knowledge Management ─────────────────────────────

    def reload_knowledge(self):
        """Recarga archivos .md de knowledge/ (hot-reload)."""
        self.knowledge.reload()
        print("[Agent] 🔄 Conocimiento recargado")

    # ── Internals ────────────────────────────────────────

    @staticmethod
    def _load_skills(skills_dir: str) -> dict[str, str]:
        """Carga todos los archivos .md de skills/ en un diccionario."""
        skills: dict[str, str] = {}
        path = Path(skills_dir)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        for md_file in path.glob("*.md"):
            name = md_file.stem  # nombre sin extensión
            skills[name] = md_file.read_text("utf-8")
        print(f"[Agent] 🎯 {len(skills)} skills cargadas de {path}")
        if not skills:
            print("[Agent] ⚠️ No se encontraron skills. Crea .md en agent/skills/")
        return skills
