"""
Rate Limiter — Token bucket algorithm.
Controla requests por minuto (RPM) para no saturar ChatGPT Web.
"""

import time
import asyncio
from typing import Optional


class RateLimiter:
    """
    Token bucket con recarga configurable.

    Uso:
        limiter = RateLimiter(rpm=10, burst=3)
        async with limiter:
            await bridge.send(...)
    """

    def __init__(self, rpm: int = 10, burst: int = 3):
        self._rate = rpm / 60.0         # tokens por segundo
        self._burst = burst              # máximo tokens acumulables
        self._tokens = float(burst)      # tokens disponibles
        self._last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    @property
    def available(self) -> float:
        return self._tokens

    @property
    def stats(self) -> dict:
        return {
            "rpm": int(self._rate * 60),
            "burst": self._burst,
            "available_tokens": round(self._tokens, 1),
        }

    async def acquire(self) -> bool:
        """Intenta consumir 1 token. Bloquea si no hay disponibles."""
        async with self._lock:
            self._refill()
            if self._tokens >= 1.0:
                self._tokens -= 1.0
                return True
            wait_time = (1.0 - self._tokens) / self._rate
            await asyncio.sleep(wait_time)
            self._refill()
            self._tokens -= 1.0
            return True

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, *args):
        pass

    def _refill(self):
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self._burst, self._tokens + elapsed * self._rate)
        self._last_refill = now
