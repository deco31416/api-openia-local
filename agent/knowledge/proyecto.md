# ChatGPT Web Bridge — Documentación del proyecto

## Arquitectura

Este proyecto implementa un puente local entre clientes compatibles con la API de OpenAI y la interfaz web de ChatGPT. Usa Playwright para automatizar un navegador Chromium que interactúa con chatgpt.com.

### Stack tecnológico

- **Python 3.11+** con type hints completos
- **FastAPI** como servidor HTTP asíncrono
- **Playwright** para automatización de navegador
- **Pydantic v2** para validación de esquemas
- **tiktoken** para conteo real de tokens (cl100k_base)

### Principios de diseño

1. **Cero dependencias pesadas**: sin ChromaDB, FAISS, ni transformers.
2. **Modular**: cada archivo .py < 200 líneas, una responsabilidad.
3. **Local-first**: todo corre en localhost, nunca expuesto a internet.
4. **OpenAI-compatible**: mismo SDK, mismos schemas, mismos endpoints.

## Endpoints

- `GET /health` — Diagnóstico de 9 componentes
- `GET /dashboard` — Dashboard web en tiempo real
- `GET /v1/models` — Modelos disponibles
- `POST /v1/chat/completions` — Chat (stream=True para SSE)
- `GET /v1/conversations` — Chats guardados
- `GET /v1/conversations/{id}/usage` — Costo por chat
- `DELETE /v1/conversations/{id}` — Eliminar chat
- `GET /v1/usage` — Uso global acumulado
- `DELETE /v1/usage` — Reiniciar contador

## Seguridad

- Rate limiting: 10 RPM por defecto (configurable)
- Cola FIFO: 1 request concurrente, 10 en espera
- AntiBan: simulación de comportamiento humano
- Graceful shutdown: drena requests antes de apagar
- Watchdog: auto-recuperación ante caídas de UI

## Configuración

Editar `config.yaml` para personalizar puerto, rate limits, antiban, streaming.
