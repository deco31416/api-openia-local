"""
Selector Recovery — Fallback automático cuando ChatGPT cambia su UI.
Prueba selectores alternativos si el principal falla.
"""

import asyncio
from typing import Callable, Awaitable, Any


class SelectorRecovery:
    """
    Ejecuta acciones con reintentos usando selectores alternativos.

    Uso:
        recovery = SelectorRecovery()
        btn = await recovery.try_select(page, [
            'button[data-testid="send-button"]',
            'button[aria-label="Send prompt"]',
            'button:has-text("Send")',
        ])
    """

    def __init__(self, max_retries: int = 3, base_delay: float = 0.5):
        self._max_retries = max_retries
        self._base_delay = base_delay

    async def try_select(self, page, selectors: list[str], timeout: float = 5.0):
        """
        Prueba cada selector en orden con timeout por intento.
        Devuelve el primer elemento encontrado o None.
        """
        for attempt in range(self._max_retries):
            for selector in selectors:
                try:
                    el = await page.wait_for_selector(selector, timeout=timeout * 1000)
                    if el:
                        return el
                except Exception:
                    continue
            # Backoff entre intentos
            delay = self._base_delay * (2 ** attempt)
            await asyncio.sleep(delay)
        return None

    async def try_action(self, action: Callable[[], Awaitable[Any]], name: str = "action") -> Any:
        """Ejecuta una acción con reintentos exponenciales."""
        last_error = None
        for attempt in range(self._max_retries):
            try:
                return await action()
            except Exception as e:
                last_error = e
                delay = self._base_delay * (2 ** attempt)
                print(f"[Recovery] ⚠️ {name} falló (intento {attempt+1}/{self._max_retries}): {e}")
                await asyncio.sleep(delay)
        raise last_error or RuntimeError(f"{name} falló después de {self._max_retries} intentos")
