# Changelog

All notable changes to **ChatGPT Web Bridge** are documented in this file.

This project follows the principles of [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Dates use **ISO 8601** format: `YYYY-MM-DD`.

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

## [1.2.0] — 2026-06-04

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
