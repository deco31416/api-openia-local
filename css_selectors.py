"""
Selectores CSS para la UI de ChatGPT.
Centralizados aquí para facilitar actualización si ChatGPT cambia su HTML.
"""

# ═══════════════════════════════════════════════════════════
# Selectores principales
# ═══════════════════════════════════════════════════════════

SELECTORS: dict[str, str] = {
    "prompt_input": (
        'div[contenteditable="true"].ProseMirror, '
        "#prompt-textarea, "
        'textarea[placeholder*="Message"], '
        'textarea[placeholder*="Search"], '
        'textarea[placeholder*="Ask"], '
        "textarea[data-id]"
    ),
    "send_btn": (
        'button[data-testid="send-button"], '
        'button[aria-label="Send prompt"], '
        "button[type=\"submit\"]"
    ),
    "response_container": 'div[data-message-author-role="assistant"]',
    "stop_btn": (
        'button[data-testid="stop-button"], '
        'button[aria-label="Stop streaming"]'
    ),
    "new_chat": (
        'button:has-text("New chat"), '
        'button[aria-label="New chat"], '
        'a[href="/"]'
    ),
    "login_btn": (
        'button[data-testid="login-button"], '
        'button:has-text("Log in"), '
        'button:has-text("Sign up")'
    ),
    "model_selector": (
        'button[aria-label="Model"], '
        "button[aria-haspopup=\"menu\"]:has(svg), "
        "div[data-testid=\"model-switcher\"] button, "
        ".model-switcher button"
    ),
    "model_option_tmpl": (
        'li:has-text("{model}"), '
        "div[role=\"menuitem\"]:has-text(\"{model}\"), "
        "button:has-text(\"{model}\")"
    ),
    "current_model": (
        'button[aria-label="Model"] span, '
        "div[data-testid=\"model-switcher\"] span, "
        ".model-switcher span"
    ),
    # Imágenes generadas por ChatGPT
    "generated_image": (
        'div[data-message-author-role="assistant"] img[src*="oaidalleapiprodscus"], '
        'div[data-message-author-role="assistant"] img[alt*="Generated"], '
        'div[data-message-author-role="assistant"] img[src^="https://files."] '
    ),
    # Input de archivos
    "file_input": 'input[type="file"]',
}

# Modelos que se pueden seleccionar con nombres alternativos
MODEL_FALLBACKS: dict[str, list[str]] = {
    # o3 5.5
    "o3-5.5-instant": ["o3 5.5 instant", "O3 5.5 Instant"],
    "o3-5.5-thinking": ["o3 5.5 thinking", "O3 5.5 Thinking"],
    # GPT family
    "o4-mini": ["o4-mini", "O4-mini", "o4 mini", "O4 Mini"],
    "gpt-4o": ["GPT-4o", "GPT-4", "gpt-4", "4o"],
    "gpt-4o-mini": ["GPT-4o mini", "GPT-4o Mini", "gpt-4-mini", "4o-mini"],
    "gpt-4.1": ["GPT-4.1", "gpt-4.1", "4.1"],
}


def resolve_model_name(requested: str) -> list[str]:
    """Devuelve todos los nombres alternativos para un modelo dado."""
    requested_lower = requested.lower().strip()
    for key, aliases in MODEL_FALLBACKS.items():
        if requested_lower == key.lower():
            return aliases
    return [requested]
