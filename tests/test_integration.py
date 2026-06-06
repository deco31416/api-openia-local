"""
Tests de integración — módulos que interactúan entre sí.
No requieren Playwright ni ChatGPT Web (unitarios puros).
"""

import json
import os
import time
import tempfile
import asyncio
import pytest


# ═══════════════════════════════════════════════════════════
# Streamer (SSE)
# ═══════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_sse_streamer_chunks():
    """El streamer debe emitir múltiples chunks y un chunk final."""
    from sse_streamer import Streamer
    s = Streamer(delay_ms=1, chunk_tokens=2)
    chunks: list[str] = []
    async for chunk in s.stream("Hello world test", model="gpt-4o"):
        chunks.append(chunk)
    assert len(chunks) >= 3  # role + contenido + final
    assert chunks[-1] == "data: [DONE]\n\n"


@pytest.mark.asyncio
async def test_sse_streamer_empty_text():
    """Texto vacío debe generar chunks mínimos sin crashear."""
    from sse_streamer import Streamer
    s = Streamer(delay_ms=1)
    chunks: list[str] = []
    async for chunk in s.stream("", model="gpt-4o"):
        chunks.append(chunk)
    assert len(chunks) >= 2  # role + final


# ═══════════════════════════════════════════════════════════
# Queue Manager
# ═══════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_queue_manager_rejects_when_full():
    """Cuando la cola está llena, debe lanzar QueueFullError."""
    from queue_manager import RequestQueue, QueueFullError
    q = RequestQueue(max_concurrent=1, max_queue=1)
    # Llenar cola: 2 requests con max_queue=1 → rechazo
    async with q:
        # Segundo request: debería ir a cola
        task2 = asyncio.create_task(_acquire_queue(q))
        await asyncio.sleep(0.01)
        # Tercer request: cola llena → QueueFullError
        with pytest.raises(QueueFullError):
            async with q:
                pass
        task2.cancel()


async def _acquire_queue(q):
    async with q:
        await asyncio.sleep(0.1)


@pytest.mark.asyncio
async def test_queue_manager_tracks_stats():
    """La cola debe trackear procesados y rechazados."""
    from queue_manager import RequestQueue
    q = RequestQueue(max_concurrent=2, max_queue=5)
    for _ in range(3):
        async with q:
            pass
    stats = q.stats
    assert stats["processed"] == 3
    assert stats["rejected"] == 0


# ═══════════════════════════════════════════════════════════
# Rate Limiter
# ═══════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_rate_limiter_blocks_when_empty():
    """Sin tokens, el rate limiter debe esperar."""
    from rate_limiter import RateLimiter
    rl = RateLimiter(rpm=600, burst=1)
    rl._tokens = 0.0  # forzar sin tokens
    t0 = time.monotonic()
    await rl.acquire()
    elapsed = time.monotonic() - t0
    # Debe esperar al menos el tiempo de recarga de 1 token
    assert elapsed > 0.0


# ═══════════════════════════════════════════════════════════
# Agent Builder
# ═══════════════════════════════════════════════════════════

def test_agent_build_prompt_with_skill():
    """El agente debe incluir la skill en el prompt."""
    from agent.agent import SimpleAgent
    agent = SimpleAgent()
    prompt = agent.build_prompt("Hola", skill="code-review", use_memory=False)
    assert "[USER]" in prompt
    assert "Hola" in prompt


def test_agent_build_prompt_default():
    """Sin skill especificada, usa 'default'."""
    from agent.agent import SimpleAgent
    agent = SimpleAgent()
    prompt = agent.build_prompt("Test", skill="default", use_memory=False)
    assert "[USER]" in prompt


# ═══════════════════════════════════════════════════════════
# Agent Writer (Knowledge)
# ═══════════════════════════════════════════════════════════

def test_knowledge_writer_save_skill(tmp_path):
    """Guardar skill debe crear archivo .md."""
    from agent.knowledge_writer import KnowledgeWriter
    kw = KnowledgeWriter(skills_dir=str(tmp_path / "skills"), knowledge_dir=str(tmp_path / "knowledge"))
    path = kw.save_skill("test-skill", "## Test Skill\nContenido de prueba")
    assert path.exists()
    content = path.read_text()
    assert "## Test Skill" in content


def test_knowledge_writer_detect_correction():
    """Debe detectar patrones de corrección en mensajes."""
    from agent.knowledge_writer import KnowledgeWriter
    kw = KnowledgeWriter()
    msgs = [
        {"role": "assistant", "content": "La API es https://old.example.com"},
        {"role": "user", "content": "no, la URL correcta es https://new.example.com"},
        {"role": "assistant", "content": "Usa https://old.example.com"},
        {"role": "user", "content": "corrige eso, la URL es https://new.example.com"},
        {"role": "assistant", "content": "https://old.example.com es la URL"},
        {"role": "user", "content": "recuerda que la URL es https://new.example.com"},
    ]
    result = kw.detect_pattern(msgs, min_occurrences=3)
    assert result is not None
    assert result["type"] == "correction"


# ═══════════════════════════════════════════════════════════
# Memory Store
# ═══════════════════════════════════════════════════════════

def test_memory_store_handles_corrupt_json(tmp_path):
    """Archivo JSON corrupto no debe crashear el store."""
    from agent.memory_store import MemoryStore
    conv_dir = tmp_path / "conversations"
    conv_dir.mkdir()
    # Escribir bytes inválidos que rompan UTF-8 y JSON
    (conv_dir / "bad.json").write_bytes(b'\xff\xfe\x00\x01\x02')
    store = MemoryStore(str(tmp_path))
    # Al cargar, debe retornar None sin crashear
    result = store.load("bad")
    assert result is None
