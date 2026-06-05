# 🗺️ Roadmap

Planned improvements and feature pipeline for **ChatGPT Web Bridge**.

Status legend: `🔵 Planned` · `🟡 In Progress` · `🟢 Done`

---

## 🟢 v1.x — Current (2026-06-04)

- [x] OpenAI-compatible `/v1/chat/completions` + `/v1/models`
- [x] Playwright browser automation (headless + visible)
- [x] Model auto-detection and switching (GPT-4o, o3, o4-mini, GPT-4.1)
- [x] Image upload to ChatGPT Web + DALL-E extraction
- [x] Conversation persistence (`conversations.json`, `SessionStore`)
- [x] Real token counting with `tiktoken` (`cl100k_base`)
- [x] Cost tracker with per-model pricing + global/per-chat views
- [x] Modular architecture (13 `.py` files, all <200 lines)
- [x] Windows launchers (`run.ps1`, `run.bat`)
- [x] MIT license, ISO 8601 changelog, conventional commits
- [x] Enhanced `/health` endpoint with component diagnostics

---

## � v2.0 — Reliability & Robustness ✅ DONE

- [x] Request queue: FIFO queue with configurable concurrency (`queue_manager.py`)
- [x] Local rate limiting: token bucket, configurable RPM (`rate_limiter.py`)
- [x] Selector recovery: auto-fallback + exponential backoff (`selector_recovery.py`)
- [x] Structured error codes: standard HTTP errors + Retry-After (`error_codes.py`)
- [x] Graceful shutdown: drain in-flight requests on SIGINT/SIGTERM (`graceful_shutdown.py`)
- [x] Conversation isolation: `X-Conversation-ID` header (strict mode via session store)
- [x] Better logging and diagnostics: health endpoint with 9 components
- [x] Modular extraction: `chat_handler.py` separates business logic from routing

---

## 🔵 v2.1 — OpenAI Parity

- [ ] **Streaming**: SSE `stream=True` in `/v1/chat/completions`
- [ ] **Function calling**: parse `tools`/`tool_calls` from ChatGPT Web responses
- [ ] **Vision mode**: full `image_url` content part support in chat completions
- [ ] **Embeddings**: `/v1/embeddings` endpoint (if web supports it)
- [ ] **More parameters**: `top_p`, `n`, `stop`, `presence_penalty`, `frequency_penalty`

---

## 🔵 v2.2 — Observability

- [ ] **Structured logging**: JSON log format with request IDs for tracing
- [ ] **Metrics dashboard**: local `/metrics` endpoint (Prometheus-compatible)
- [ ] **Request timing**: `X-Response-Time` header per request
- [ ] **Error diagnostics**: detailed error payload with `error_code`, `component`, `selector`
- [ ] **Session health**: `/health` shows browser uptime, session expiry, memory usage

---

## 🔵 v3.0 — Multi-Browser & Platform

- [ ] **Docker support**: `Dockerfile` + `docker-compose.yml`
- [ ] **macOS/Linux testing**: full cross-platform validation
- [ ] **Firefox/WebKit**: optional non-Chromium browser engines
- [ ] **Multi-tab support**: parallel conversations in separate browser tabs
- [ ] **Plugin system**: hook-based middleware for custom transformations

---

## 📐 Design Principles

| Principle | Why |
|---|---|
| **No file >200 lines** | Single responsibility, easy to audit |
| **OpenAI-compatible schema** | Drop-in replacement for any OpenAI SDK |
| **Browser-first** | Real ChatGPT Web session = full capabilities |
| **Local only** | Never exposed to internet, `localhost` binding |
| **No API key required** | Uses existing ChatGPT web login |

---

## 🤝 Contributions

Want to help with any of these? See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for guidelines.

---

<div align="center">
  <sub>© 2024-2026 deco31416.com — All rights reserved.</sub>
</div>
