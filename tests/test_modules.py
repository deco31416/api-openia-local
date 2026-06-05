"""
Tests unitarios para módulos puros (sin dependencias de Playwright).
"""

import sys
import os
import json
import time
import asyncio
import pytest


# ── token_counter ─────────────────────────────────────────

def test_count_tokens_english():
    from token_counter import count_tokens
    assert count_tokens("Hello world") == 2
    assert count_tokens("") == 0  # texto vacío = 0 tokens
    assert count_tokens("This is a longer sentence with more tokens") > 3


# ── cost_tracker ─────────────────────────────────────────

def test_cost_tracker_track_and_summary(tmp_path):
    from cost_tracker import CostTracker, get_price
    ct = CostTracker(filepath=str(tmp_path / "usage.json"))
    ct.track("gpt-4o", 1000, 5000)
    ct.track("gpt-4o-mini", 2000, 3000)
    summary = ct.summary()
    assert summary["totals"]["total_tokens"] == 11000
    assert summary["totals"]["calls"] == 2
    assert summary["by_model"]["gpt-4o"]["cost_total_usd"] > 0
    assert summary["by_model"]["gpt-4o-mini"]["cost_total_usd"] < summary["by_model"]["gpt-4o"]["cost_total_usd"]


def test_get_price():
    from cost_tracker import get_price
    ci, co, ct = get_price("gpt-4o", 1_000_000, 1_000_000)
    assert ci == 2.50  # $2.50/1M input
    assert co == 10.00  # $10/1M output
    assert ct == 12.50


# ── error_codes ──────────────────────────────────────────

def test_error_response():
    from error_codes import error_response
    code, body = error_response("QUEUE_FULL", retry_after=5)
    assert code == 429
    assert body["error"]["code"] == "QUEUE_FULL"
    assert body["error"]["retry_after_seconds"] == 5


def test_error_response_unknown():
    from error_codes import error_response
    code, body = error_response("NONEXISTENT")
    assert code == 500
    assert "desconocido" in body["error"]["message"].lower() or "unknown" in body["error"]["message"].lower()


# ── session_store ────────────────────────────────────────

def test_session_store_save_and_list(tmp_path):
    from session_store import SessionStore
    store = SessionStore(filepath=str(tmp_path / "conv.json"))
    store.save("abc123", "gpt-4o", "Hola mundo", 10, 50)
    time.sleep(0.001)  # timestamp distinto
    store.save("def456", "o3", "Explain Rust", 20, 100)
    data = store.list_all()
    assert len(data) == 2
    ids = {c["conversation_id"] for c in data}
    assert "abc123" in ids
    assert "def456" in ids
    for c in data:
        if c["conversation_id"] == "def456":
            assert c["prompt_tokens"] == 20
            assert c["total_tokens"] == 120


def test_session_store_delete(tmp_path):
    from session_store import SessionStore
    store = SessionStore(filepath=str(tmp_path / "conv.json"))
    store.save("abc", "gpt-4o", "test", 5, 5)
    store.delete("abc")
    assert store.get("abc") is None
    assert len(store.list_all()) == 0


# ── antiban ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_antiban_human_mode():
    from antiban import AntiBan
    ab = AntiBan(human_mode=True, wpm=120, min_think=0.01, max_think=0.02)
    t0 = time.monotonic()
    await ab.thinking_pause()
    await ab.typing_delay(50)
    await ab.inter_request_pause()
    elapsed = time.monotonic() - t0
    assert 0.01 < elapsed < 10.0  # human_mode con delays


@pytest.mark.asyncio
async def test_antiban_off_mode():
    from antiban import AntiBan
    ab = AntiBan(human_mode=False)
    t0 = time.monotonic()
    await ab.thinking_pause()
    await ab.typing_delay(10000)
    await ab.inter_request_pause()
    elapsed = time.monotonic() - t0
    assert elapsed < 0.1  # instantáneo


# ── models ────────────────────────────────────────────────

def test_chat_completion_request_all_params():
    from models import ChatCompletionRequest, ChatMessage
    req = ChatCompletionRequest(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Hello"}],
        max_tokens=100, temperature=0.7, top_p=0.9, n=1,
        stream=False, stop=["###"], presence_penalty=0.5,
        frequency_penalty=0.3, user="test", seed=42,
        response_format={"type": "json_object"},
        logprobs=True, top_logprobs=3,
    )
    assert req.model == "gpt-4o"
    assert len(req.messages) == 1
    assert req.seed == 42


def test_chat_completion_response():
    from models import ChatCompletionResponse, ChatChoice, ChatMessage, UsageInfo
    resp = ChatCompletionResponse(
        id="chatcmpl-xxx", created=123, model="gpt-4o",
        choices=[ChatChoice(index=0, message=ChatMessage(role="assistant", content="Hi!"))],
        usage=UsageInfo(prompt_tokens=2, completion_tokens=1, total_tokens=3),
    )
    assert resp.object == "chat.completion"
    assert resp.choices[0].message.content == "Hi!"


# ── graceful_shutdown ────────────────────────────────────

@pytest.mark.asyncio
async def test_shutdown_tracker():
    from graceful_shutdown import GracefulShutdown, ShuttingDownError
    sd = GracefulShutdown(timeout=1.0)
    assert not sd.shutting_down
    assert sd.active_requests == 0

    async with sd.track():
        assert sd.active_requests == 1

    assert sd.active_requests == 0


# ── css_selectors ─────────────────────────────────────────

def test_resolve_model_name():
    from css_selectors import resolve_model_name
    assert "GPT-4o" in resolve_model_name("gpt-4o")
    assert "o3" in resolve_model_name("o3")
    assert resolve_model_name("unknown-model") == ["unknown-model"]


# ── config files ──────────────────────────────────────────

def test_gitignore_exists():
    assert os.path.exists(".gitignore")


def test_requirements_exists():
    assert os.path.exists("requirements.txt")


def test_readme_exists():
    assert os.path.exists("README.md")


def test_license_exists():
    assert os.path.exists("LICENSE")
