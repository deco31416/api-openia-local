"""
Contador de tokens usando tiktoken (mismo tokenizer de OpenAI).
Reemplaza la estimación burda len(text)//4 por conteo real.
"""

from typing import Optional

# Lazy load: solo importa si se necesita
_encoder: Optional[object] = None


def _get_encoder():
    """Obtiene el encoder cl100k_base (GPT-4, GPT-4o, o3, etc.)."""
    global _encoder
    if _encoder is None:
        try:
            import tiktoken
            _encoder = tiktoken.get_encoding("cl100k_base")
        except ImportError:
            return None
    return _encoder


def count_tokens(text: str) -> int:
    """
    Cuenta tokens reales usando el mismo tokenizer de OpenAI.
    Fallback a estimación len/4 si tiktoken no está instalado.
    """
    enc = _get_encoder()
    if enc is not None:
        return len(enc.encode(text))
    return max(1, len(text) // 4)
