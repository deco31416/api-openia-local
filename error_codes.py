"""
Error Codes — Códigos de error estructurados compatibles con OpenAI.
Devuelve errores con códigos, mensajes y metadatos estándar.
"""

from typing import Optional


# ═══════════════════════════════════════════════════════════
# Catálogo de errores
# ═══════════════════════════════════════════════════════════

ERROR_CODES = {
    "QUEUE_FULL":        (429, "Cola de requests llena. Reintenta en unos segundos."),
    "RATE_LIMITED":      (429, "Límite de requests por minuto alcanzado."),
    "BRIDGE_DOWN":       (503, "Bridge no disponible. ¿Iniciaste el servidor?"),
    "AUTH_REQUIRED":     (401, "Sesión de ChatGPT no autenticada."),
    "TIMEOUT":           (504, "Timeout esperando respuesta de ChatGPT Web."),
    "SELECTOR_FAIL":     (502, "No se pudo interactuar con ChatGPT Web. ¿Cambió la UI?"),
    "NO_RESPONSE":       (502, "ChatGPT Web no devolvió respuesta."),
    "BAD_REQUEST":       (400, "Request mal formado."),
    "INTERNAL_ERROR":    (500, "Error interno del bridge."),
    "SHUTTING_DOWN":     (503, "Servidor en proceso de apagado. No se aceptan requests."),
}


def error_response(code: str, detail: str = "", retry_after: Optional[int] = None) -> tuple[int, dict]:
    """Construye una respuesta de error estructurada. Retorna (http_status, body)."""
    http_status, default_msg = ERROR_CODES.get(code, (500, "Error desconocido."))
    body = {
        "error": {
            "code": code,
            "message": detail or default_msg,
            "type": "chatgpt_web_bridge_error",
        }
    }
    headers = {}
    if retry_after is not None:
        body["error"]["retry_after_seconds"] = retry_after
    return http_status, body
