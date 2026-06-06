# Changelog

All notable changes to **ChatGPT Web Bridge** are documented in this file.

This project follows the principles of [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Dates use **ISO 8601** format: `YYYY-MM-DD`.

---
## [3.2.0] — 2026-06-04

### Added — Knowledge Writer (el agente que también escribe)

- **`agent/knowledge_writer.py`**: generación de archivos `.md` manual y automática.
  - `save_skill()` / `save_knowledge()` / `save_summary()`.
  - `detect_pattern()`: detecta correcciones recurrentes y sugiere guardarlas.
- **Comandos `!save`**: `!save skill <nombre>`, `!save knowledge <nombre>`, `!save summary`.
  - El contenido se toma de la respuesta del asistente.
- **Auto-sugerencias**: después de cada respuesta, el agente detecta patrones y sugiere guardar.
- **`.gitignore`**: excluye archivos personales en `agent/knowledge/`, `agent/skills/`, `agent/memory/`.
  - Solo los 7 archivos de ejemplo se versionan.
- **README**: añadida la frase filosófica del proyecto.

### Changed

- `agent.py` actualizado con `save_skill()`, `save_knowledge()`, `detect_learning()`.
- `server.py` endpoint `/v1/agent/chat` procesa comandos `!save` + sugerencias.

---
## [3.0.0] — 2026-06-04

### Added — Producción-Ready

- **SSE Streaming real**: `sse_streamer.py` emite tokens con tiktoken via Server-Sent Events.
  - `POST /v1/chat/completions` con `stream=True` devuelve `text/event-stream`.
  - Delay configurable (30ms), chunk de 1 token, formato OpenAI ChatCompletionChunk.
- **Watchdog**: `watchdog.py` monitorea salud de la página cada 30s, reintenta 3 fallos, reinicia automáticamente.
- **Session Recovery**: `session_recovery.py` guarda/restaura cookies en `session.json`.
  - Auto-save al apagar, auto-restore al arrancar.
- **Dashboard web**: `dashboard.py` — HTML servido en `GET /dashboard`.
  - Health, uso global, conversaciones, cola. Auto-refresh cada 10s.
- **Config YAML**: `config.yaml` con todos los parámetros (server, queue, rate, antiban, streaming, watchdog).
- **`session.json`** agregado a `.gitignore` (datos de sesión local).

### Changed

- `chat_handler.py`: soporta streaming con `stream_chat()`.
- `server.py`: endpoint `/v1/chat/completions` acepta `stream=True`, watchdog + session recovery integrados.

---

## [2.3.0] — 2026-06-04

### Added

- **Test suite**: 17 tests unitarios con `pytest` + `pytest-asyncio` + `pytest-cov`.
- `tests/test_modules.py`: cobertura de token_counter, cost_tracker, error_codes, session_store, antiban, models, graceful_shutdown, css_selectors.
- **Makefile**: `test`, `coverage`, `lint`, `typecheck`, `clean`, `run`, `run-headless`.
- `pytest`, `pytest-asyncio`, `pytest-cov` en `requirements.txt`.

### Changed

- `graceful_shutdown.py`: `track()` ahora es `def` (no `async def`).
- Tests arreglados para `session_store` ordenamiento y `antiban` timing.

---
## [3.3.0] — 2026-06-04

### Added — API Key + Multi-host

- **Middleware `X-API-Key`**: autenticación simple sin dependencias extra.
  - `BRIDGE_API_KEY` en `.env` o `--api-key` en CLI.
  - Excluye `/health`, `/dashboard`, `/docs` para diagnóstico público.
- **`--host`**: permite escuchar en `0.0.0.0` para servir en red local.
- **`.env.example`**: template de configuración con variables documentadas.
- **README**: sección "Exponer en red local o internet" con recomendaciones.
- **README**: frase _"Si pierdo la llave, cambio la cerradura. Nadie se lleva mi jardín."_

### Changed

- `server.py` escucha en `127.0.0.1` por defecto (antes `0.0.0.0`).

---
## [2.2.0] — 2026-06-04

### Added

- **`antiban.py`**: simula comportamiento humano para evitar detección y baneo.
- `thinking_pause()`: delay aleatorio 0.5-3s antes de escribir (simula "pensar").
- `typing_delay()`: delay proporcional a longitud del texto (~60 WPM).
- `reading_pause()`: pausa 1-4s después de recibir respuesta (simula "leer").
- `inter_request_pause()`: delay 1-3s entre requests, 5-15s cada 5 requests.
- Integrado en `chat_handler.py` con `human_mode=True` por defecto.

### Why

- ChatGPT detecta bots por velocidad constante, sin pausas, sin variabilidad.
- AntiBan inyecta comportamiento humano real para evitar bans a alta velocidad.

---

## [2.1.0] — 2026-06-04

### Added

- **Full OpenAI API compatibility**: todos los parámetros del spec oficial.
- `ContentPart`, `FunctionCall`, `ToolCall`, `ToolMessage` models.
- `ResponseFormat` (text/json_object/json_schema), `StreamOptions`.
- `seed`, `logprobs`, `top_logprobs`, `logit_bias`, `tools`, `tool_choice`.
- `parallel_tool_calls`, `max_completion_tokens`.
- `ChatCompletionChunk` para streaming SSE chunks.
- `system_fingerprint`, `service_tier` en ChatCompletionResponse.
- `prompt_tokens_details`, `completion_tokens_details` en UsageInfo.
- Validación de rangos Pydantic (`ge=0, le=2`) en temperature/presence_penalty.

### Changed

- `models.py` completo reescrito con tipos fuertes y specs oficiales OpenAI.
- `ChatMessage.content` ahora acepta `List[ContentPart]` tipado (antes `List[dict]`).

---

## [3.0.0] — 2026-06-04

### Added — Reliability & Robustness (v2.0 roadmap completo)

- `queue_manager.py`: cola FIFO asíncrona con semáforo de concurrencia (max_concurrent=1, max_queue=10).
- `rate_limiter.py`: token bucket con RPM configurable (default 10 RPM, burst=3).
- `selector_recovery.py`: reintentos con backoff exponencial + fallback de selectores.
- `error_codes.py`: catálogo estructurado (QUEUE_FULL, RATE_LIMITED, TIMEOUT, BRIDGE_DOWN, etc).
- `graceful_shutdown.py`: drena requests pendientes en SIGINT/SIGTERM con timeout 30s.
- `chat_handler.py`: handler separado con toda la lógica de procesamiento de chat.
- `/health` ahora reporta queue, rate_limiter y graceful_shutdown status.

### Changed

- `server.py`: reducido de 225 → 159 líneas con integración de todos los módulos v2.0.
- Todo error usa `error_response()` con códigos estructurados + `retry_after`.
- Lifespan incluye `SHUTDOWN.register_signals()` + `wait_for_drain()`.
- `health_diagnostics.py` reporta 9 componentes (antes 5).

### Roadmap Status

- [x] Request queue handling
- [x] Local rate limiting
- [x] Selector recovery
- [x] Structured error codes
- [x] Graceful shutdown
- [x] Better logging and diagnostics

---

## [1.8.0] — 2026-06-04

### Added

- **ROADMAP.md** con pipeline de features v2.0 → v3.0.
- **health_diagnostics.py**: diagnóstico por componente (bridge, browser, tiktoken, session store).
- `ComponentStatus` model en `models.py` para reportes de estado estructurados.
- `/health` ahora muestra `components[]`, `errors[]`, `uptime_seconds`, `version`.

### Changed

- `server.py` de 251 → 197 líneas (health extraído a `health_diagnostics.py`).
- `models.py`: `HealthResponse` enriquecido con campos de diagnóstico.
- README: link a ROADMAP.md, versión badge 1.8.0.

---

## [1.7.0] — 2026-06-04

### Added

- `routes.py` — router separado para endpoints de conversaciones y uso.
- `GET /v1/conversations/{id}/usage` — costo individual por chat.

### Changed

- `server.py` reducido de 243 a 197 líneas (rutas extraídas a `routes.py`).
- `chatgpt_bridge.py` ya no importa `session_store` (save se hace en server).
- README actualizado con todas las features v1.6.0+ y nuevos endpoints.

---

## [1.6.0] — 2026-06-04

### Added

- **Tokens por conversación**: `session_store.save()` ahora acumula `prompt_tokens` y `completion_tokens`.
- `GET /v1/conversations/{id}/usage` — costo individual de cada chat.
- `GET /v1/conversations` ahora incluye tokens y totales por chat.

### Changed

- El servidor ahora guarda tokens en el session store (el bridge solo trackea la URL).
- `cost_tracker` + `session_store` trabajan juntos: tracker global + store por chat.

---

## [1.5.0] — 2026-06-04

### Added

- **Cost Tracker**: `cost_tracker.py` acumula tokens y calcula costo en USD.
- Precios reales por modelo: GPT-4o ($2.50/$10), o3 ($10/$40), GPT-4o-mini ($0.15/$0.60), etc.
- `GET /v1/usage` — resumen de tokens acumulados + costo estimado.
- `DELETE /v1/usage` — reinicia el contador.
- `usage.json` persiste métricas entre reinicios.
- Tracker se integra automáticamente en cada `POST /v1/chat/completions`.

### Changed

- `.gitignore` ahora excluye `usage.json`.

---

## [1.4.0] — 2026-06-04

### Added

- **Session Store**: `session_store.py` persiste conversaciones en `conversations.json`.
- `GET /v1/conversations` — lista todos los chats guardados (sobrevive a reinicios).
- `DELETE /v1/conversations/{id}` — elimina un chat del store.
- Auto-guardado: cada `send()` persiste `conversation_id` + modelo + resumen.
- `goto_conversation()` solo navega si no estás ya en ese chat.

### Changed

- `.gitignore` ahora excluye `conversations.json` (datos locales del usuario).

---

## [1.3.0] — 2026-06-04

### Added

- **tiktoken** para conteo REAL de tokens (mismo tokenizer `cl100k_base` de OpenAI).
- `token_counter.py`: `count_tokens()` con fallback automático a `len/4`.

### Changed

- **Velocidad optimizada**: `Prompter` usa `fill()` en lugar de `type(delay=10)`.
- Polling reducido de 800ms a 300ms para detección de fin de respuesta.
- `goto_conversation()` ahora detecta si ya estás en el chat y no navega.
- Waits reducidos: `asyncio.sleep(2)` → `0.5`, `sleep(0.3)` → 0.

---

## [3.7.0] — 2026-06-05

### Changed — Modelos simplificados: Instant + Thinking

- **o3 5.5 Instant + Thinking**: solo 2 variantes por versión.
- **o3 5.4 Instant + Thinking**: misma estructura.
- Lucide React en ModelSelector: `Brain` (Thinking), `Zap` (Instant).
- `server.py`, `css_selectors.py`, `cost_tracker.py`, `ModelSelector`, `ChatBox` sincronizados.

---

## [3.6.0] — 2026-06-05

### Changed — Lucide React icons

- **Emojis reemplazados por Lucide React** en todos los componentes.
- `Navbar`: `Brain`, `Circle` con color dinámico por estado.
- `HealthCard`: `Heart`, `ShieldCheck`, `ShieldAlert`, `ShieldX`, `Check`, `X`, `AlertTriangle`.
- `UsageCard`: `BarChart3`, `DollarSign`.
- `ConversationsList`: `MessagesSquare`, `ExternalLink`.
- `QueuePanel`: `ListOrdered`, `CheckCircle`, `AlertCircle`.
- `ModelSelector`: `Cpu`, `Check`.
- `ChatBox`: `Send`, `Loader2` (spinner animado).
- `ErrorLog`: `AlertTriangle`.
- `ui/Card`: `title` ahora acepta `ReactNode` (compatible con iconos).
- `ui/Stat`: `value` ahora acepta `ReactNode` (compatible con iconos).

---

## [3.6.0] — 2026-06-05

### Added — Nuevos modelos o3 + thinking_effort

- **o3 5.2, 5.3, 5.4, 5.5**: generación actual de modelos o3.
- **o3 Instant**: modo rápido, menor costo.
- **o3 Pro**: modo avanzado, razonamiento profundo.
- `thinking_effort` en `ChatCompletionRequest`: `low`, `medium`, `high`.
- Precios actualizados en `cost_tracker.py` para todos los modelos.
- `css_selectors.py`: fallbacks de selector para nuevos modelos.
- `server.py`: `GET /v1/models` incluye los 11 modelos.
- `ModelSelector` + `ChatBox`: UI con los nuevos modelos.

---

## [3.5.0] — 2026-06-05

### Added — Dashboard full componentizado

- **`Navbar.tsx`**: barra de navegación con estado, uptime y versión.
- **`QueuePanel.tsx`**: cola de requests en tiempo real con indicador visual.
- **`ModelSelector.tsx`**: selector de modelo (GPT-4o, o3, o4-mini, GPT-4.1).
- **`ChatBox.tsx`**: enviar prompts desde el dashboard al bridge.
- **`ErrorLog.tsx`**: últimos errores del bridge en tiempo real.
- **`ui/Card.tsx`** + **`ui/Stat.tsx`** + **`ui/Loading.tsx`**: componentes UI reutilizables.
- **`ui/index.ts`**: barrel exports para imports limpios.
- **`page.tsx`** reescrito con todos los componentes integrados.

### Changed

- `HealthCard`, `UsageCard`, `ConversationsList`: refactorizados para usar `ui/Card` + `ui/Stat` + `ui/Loading`.
- Todos los componentes usan `API_BASE` por variable de entorno.
- `lib/api.ts` mantenido como helper tipado adicional.

---

## [3.4.0] — 2026-06-05

### Added — Next.js TypeScript Dashboard

- **`dashboard/`**: Next.js + TypeScript + Tailwind CSS.
  - `src/components/HealthCard.tsx`: estado del bridge en tiempo real.
  - `src/components/UsageCard.tsx`: tokens acumulados + costo USD.
  - `src/components/ConversationsList.tsx`: lista de chats con links.
  - `src/lib/api.ts`: cliente HTTP tipado para la API del bridge.
  - `src/lib/theme.ts`: tokens de diseño centralizados + `cn()` helper.
  - `src/types/api.ts`: tipos TypeScript para todas las respuestas.
  - `src/app/globals.css`: tema oscuro con variables CSS.
  - `pnpm` como gestor de paquetes.

---

## [3.4.0] — 2026-06-06

### Fixed (Auditoría — 9 bugs y deudas técnicas)

- `_last_user_text` duplicada eliminada de `server.py`.
- `server.py` 329 → 202 líneas (`agent_handler.py` extraído).
- `ChatCompletionChunk` campos duplicados eliminados.
- `antiban.reading_pause()` ahora activo en `chat_handler.py`.
- `get_bridge()` dead code eliminado.
- `image_handler.py`: tempfile limpia con `os.unlink()`.
- `selector_recovery.py` integrado en `Prompter` como fallback.
- `recall()` expuesto: `GET /v1/agent/memory/{id}`.
- `session_recovery.restore()` activado en arranque.

### Added

- `agent_handler.py`: router del agente (136 líneas).
- `SelectorRecovery` integrado con fallback `fill()` → `type()`.

---

## [3.3.0] — 2026-06-04

### Added

- **Conversation tracking**: el bridge ahora lee y guarda el `conversation_id` de ChatGPT Web.
- `X-Conversation-ID` header en la respuesta para continuar chats existentes.
- `X-Conversation-URL` header con enlace directo a la conversación en `chatgpt.com/c/{id}`.
- `prompter.get_conversation_id()` extrae el UUID de la URL actual.
- `prompter.goto_conversation(id)` navega directamente a un chat existente.
- Parámetro `conversation_id` en `bridge.send()` para reanudar conversaciones previas.

---

## [1.1.0] — 2026-06-04

### Added

- **Image support**: upload images to ChatGPT Web and extract DALL-E generated images.
- `ImageHandler` module for base64 decode, file upload via Playwright, and DOM extraction.
- Multimodal response format: generated images returned as `image_url` parts in the content array.
- **Model switching**: `ModelManager` reads active model from ChatGPT Web UI and switches programmatically.
- `resolve_model_name()` with fallback aliases for all supported models.
- **Modular architecture**: codebase split into 9 single-responsibility modules, no file over 175 lines.
- `BrowserManager`, `AuthManager`, `Prompter`, `ModelManager` — each under 80 lines.
- `css_selectors.py` centralized selector definitions for easier UI-update maintenance.
- `selectors.py` renamed to `css_selectors.py` to avoid stdlib conflict.

### Changed

- `chatgpt_bridge.py` refactored from 307 lines to 98-line orchestrator.
- `server.py` updated for `bridge.send()` returning `(text, model, images)`.
- API response `model` field now reflects the **actual** model used in ChatGPT Web.

---

## [1.0.0] — 2026-06-04

### Added

* Initial public release of **ChatGPT Web Bridge** by **deco31416.com**.

* Local OpenAI-compatible API server powered by **FastAPI**.

* Browser automation bridge using **Playwright** to interact with ChatGPT Web at `chatgpt.com`.

* OpenAI-compatible endpoint:

  ```http
  POST /v1/chat/completions
  ```

* Model listing endpoint:

  ```http
  GET /v1/models
  ```

* Health check endpoint:

  ```http
  GET /health
  ```

* Support for OpenAI-style request and response schemas.

* Pydantic v2 models for request validation and structured API responses.

* Singleton-based `ChatGPTBridge` lifecycle to reuse the browser session.

* Support for visible browser mode for login and debugging.

* Support for headless browser mode for normal local operation.

* CLI support for configurable server port.

* CLI support for browser visibility control.

* Basic token usage estimation based on character count.

* Local browser session persistence through Playwright profile data.

* Windows bootstrap scripts:

  ```text
  run.ps1
  run.bat
  ```

* Dependency list with pinned versions in:

  ```text
  requirements.txt
  ```

* Project documentation suite:

  * `README.md`
  * `CHANGELOG.md`
  * `CONTRIBUTING.md`
  * `LICENSE`

### Security

* Server is designed for **local use only**.
* Default operation is intended for `localhost`, not public internet exposure.
* No OpenAI API key is required by the bridge.
* Uses the user’s existing authenticated ChatGPT Web session.
* Added documentation warnings about:

  * Session protection
  * Browser profile sensitivity
  * Public exposure risks
  * Rate-limit and abuse detection risks
  * Experimental nature of browser automation

### Documentation

* Added full README with:

  * Project overview
  * Architecture diagram
  * Quick start guide
  * API reference
  * Client integration examples
  * Security considerations
  * Troubleshooting section
  * Branding notice for **deco31416.com**

* Added MIT License under:

  ```text
  deco31416.com
  ```

* Added contribution guidelines with local-first and security-conscious development rules.

### Known Limitations

* The bridge depends on ChatGPT Web UI behavior, which may change without notice.
* CSS selectors or DOM structure changes may break automation.
* The requested model ID is accepted for compatibility, but the actual model behavior depends on the active ChatGPT Web session.
* Streaming behavior may not fully match the official OpenAI API.
* Token usage is estimated, not calculated by the official tokenizer.
* This project is not intended for production or public API hosting.

---

## Change Types

This changelog uses the following categories:

| Type                | Meaning                                       |
| ------------------- | --------------------------------------------- |
| `Added`             | New features or new functionality.            |
| `Changed`           | Updates to existing behavior.                 |
| `Deprecated`        | Features planned for removal.                 |
| `Removed`           | Features removed from the project.            |
| `Fixed`             | Bug fixes and corrections.                    |
| `Security`          | Security-related changes or hardening.        |
| `Documentation`     | Documentation-only changes.                   |
| `Known Limitations` | Current technical or operational limitations. |

---

## Versioning Policy

This project uses semantic versioning:

```text
MAJOR.MINOR.PATCH
```

* `MAJOR` changes may introduce breaking behavior.
* `MINOR` changes add functionality in a backward-compatible way.
* `PATCH` changes fix bugs, improve documentation, or make small safe improvements.

---

## Project Ownership

**ChatGPT Web Bridge** is maintained under the **deco31416.com** name.

The software is released under the MIT License, but the **deco31416.com** name, domain, identity, branding, logos, and public reputation are not granted for misuse, impersonation, or unauthorized representation beyond required license attribution.

---

<div align="center">

<sub>© 2024-2026 deco31416.com — MIT Licensed.</sub>

</div>
