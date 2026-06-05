"""
Watchdog — Monitor de salud de la página ChatGPT Web.
Detecta caídas, cambios de UI, rate-limits visuales y reinicia automáticamente.
"""

import asyncio
import time
from typing import Optional, Callable, Awaitable


class Watchdog:
    """
    Monitorea la página de ChatGPT y toma acciones correctivas.

    Uso:
        wd = Watchdog(page, on_recovery=reload_page)
        await wd.check()  # True si la página está sana
    """

    def __init__(
        self,
        page,
        check_interval: float = 30.0,
        max_failures: int = 3,
        on_recovery: Optional[Callable[[], Awaitable[None]]] = None,
    ):
        self._page = page
        self._check_interval = check_interval
        self._max_failures = max_failures
        self._on_recovery = on_recovery
        self._failures: int = 0
        self._events: list[dict] = []
        self._running = False

    @property
    def failures(self) -> int:
        return self._failures

    @property
    def events(self) -> list[dict]:
        return self._events[-20:]  # últimos 20 eventos

    async def check(self) -> bool:
        """Verifica si la página está respondiendo. Retorna True si está sana."""
        from css_selectors import SELECTORS
        try:
            # Intentar encontrar el input principal
            el = await self._page.wait_for_selector(
                SELECTORS["prompt_input"], timeout=5_000
            )
            if el:
                self._failures = 0
                return True
        except Exception:
            pass

        # Intentar detectar captcha o bloqueo
        try:
            captcha = await self._page.query_selector(
                'iframe[src*="challenges.cloudflare.com"], '
                'iframe[src*="recaptcha"], '
                'div[class*="cf-"], '
                'h1:has-text("unusual activity"), '
                'div:has-text("Verify you are human")'
            )
            if captcha:
                self._log("captcha_detected", "⚠️ Captcha/verificación detectada")
        except Exception:
            pass

        self._failures += 1
        self._log("watchdog_fail", f"Fallo #{self._failures}: página no responde")

        if self._failures >= self._max_failures and self._on_recovery:
            self._log("recovery_triggered", f"Iniciando recuperación tras {self._failures} fallos")
            try:
                await self._on_recovery()
                self._failures = 0
                self._log("recovery_success", "Recuperación exitosa")
                return True
            except Exception as e:
                self._log("recovery_failed", str(e))
                return False

        return False

    async def start(self):
        """Inicia el watchdog en segundo plano."""
        self._running = True
        asyncio.create_task(self._loop())

    async def stop(self):
        self._running = False

    async def _loop(self):
        while self._running:
            await asyncio.sleep(self._check_interval)
            await self.check()

    def _log(self, event: str, detail: str):
        entry = {"ts": time.time(), "event": event, "detail": detail}
        self._events.append(entry)
        print(f"[Watchdog] {detail}")
