"""
RAG Engine — Búsqueda en archivos .md de la carpeta knowledge/.
Soporta keyword matching (default) y embeddings opcionales (MiniLM).
"""

import os
import re
from pathlib import Path
from typing import Optional


class RAGEngine:
    """
    Motor de búsqueda sobre archivos .md en una carpeta.
    Keyword matching por defecto. Embeddings con sentence-transformers opcional.

    Uso:
        rag = RAGEngine("agent/knowledge")
        fragments = rag.search("¿cómo hago paella?")
        context = "\n".join(fragments)
    """

    def __init__(self, knowledge_dir: str = "agent/knowledge"):
        self._dir = Path(knowledge_dir)
        self._files: dict[str, str] = {}  # filename → content
        self._model = None
        self._embeddings: dict[str, list[float]] = {}  # filename → vector
        self._load()

    # ── Carga ────────────────────────────────────────────

    def _load(self):
        """Carga todos los .md de la carpeta."""
        if not self._dir.exists():
            self._dir.mkdir(parents=True, exist_ok=True)
        self._files.clear()
        for md_file in self._dir.glob("*.md"):
            content = md_file.read_text("utf-8")
            self._files[md_file.name] = content
        print(f"[RAG] 📚 {len(self._files)} archivos cargados de {self._dir}")

    def reload(self):
        """Recarga archivos (útil si se añaden/modifican en caliente)."""
        self._embeddings.clear()
        self._load()

    # ── Búsqueda ─────────────────────────────────────────

    def search(self, query: str, top_k: int = 3, min_score: float = 0.0) -> list[str]:
        """
        Busca fragmentos relevantes en todos los archivos.
        Retorna lista de fragmentos (máximo `top_k`), ordenados por relevancia.
        """
        if not self._files:
            return []

        if self._model is not None:
            return self._search_embeddings(query, top_k)
        return self._search_keywords(query, top_k)

    def _search_keywords(self, query: str, top_k: int) -> list[str]:
        """Keyword matching con stemming simple y penalización de stopwords."""
        stopwords = {"el", "la", "los", "las", "un", "una", "de", "del", "en", "y", "o", "a",
                     "que", "es", "por", "para", "con", "se", "no", "su", "al", "como", "más",
                     "the", "a", "an", "is", "are", "was", "were", "of", "in", "to", "and", "or"}
        query_terms = [w.lower().strip(",.?!-:;\"'") for w in query.split()
                       if w.lower().strip(",.?!-:;\"'") not in stopwords]

        if not query_terms:
            query_terms = [query.lower().strip()]

        scored: list[tuple[str, int, str]] = []
        for filename, content in self._files.items():
            content_lower = content.lower()
            # Contar matches de cada término
            score = sum(content_lower.count(term) for term in query_terms)
            if score > 0:
                # Extraer fragmento alrededor del primer match
                snippet = self._extract_snippet(content, query_terms[0])
                scored.append((filename, score, snippet))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [s[2] for s in scored[:top_k]]

    def _search_embeddings(self, query: str, top_k: int) -> list[str]:
        """Búsqueda semántica con embeddings (requiere sentence-transformers)."""
        if not self._embeddings:
            self._build_embeddings()
        query_vec = self._model.encode(query, convert_to_numpy=True)

        from scipy.spatial.distance import cosine
        scored: list[tuple[str, float, str]] = []
        for filename, vec in self._embeddings.items():
            sim = 1.0 - cosine(query_vec, vec)
            if sim > 0.3:
                snippet = self._extract_snippet(self._files[filename], query)
                scored.append((filename, sim, snippet))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [s[2] for s in scored[:top_k]]

    def _build_embeddings(self):
        """Construye embeddings para todos los archivos (solo si hay modelo)."""
        if self._model is None:
            return
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
        except ImportError:
            print("[RAG] ⚠️ sentence-transformers no instalado. Usando keywords.")
            self._model = None
            return

        for filename, content in self._files.items():
            self._embeddings[filename] = self._model.encode(content, convert_to_numpy=True)
        print(f"[RAG] 🧠 Embeddings construidos para {len(self._embeddings)} archivos")

    def enable_embeddings(self) -> bool:
        """Activa modo embeddings. Retorna True si se cargó el modelo."""
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
            self._build_embeddings()
            return True
        except ImportError:
            print("[RAG] ⚠️ pip install sentence-transformers para embeddings")
            return False

    # ── Util ─────────────────────────────────────────────

    @staticmethod
    def _extract_snippet(content: str, query: str, context_chars: int = 300) -> str:
        """Extrae un fragmento del contenido alrededor del término de búsqueda."""
        idx = content.lower().find(query.lower())
        if idx == -1:
            return content[:context_chars]
        start = max(0, idx - context_chars // 2)
        end = min(len(content), idx + context_chars // 2)
        snippet = content[start:end].strip()
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."
        return snippet
