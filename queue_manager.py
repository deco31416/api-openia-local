"""
Queue Manager — Cola FIFO con concurrencia configurable.
Evita saturar ChatGPT Web con requests simultáneos.
"""

import asyncio
import time
from typing import Optional


class RequestQueue:
    """
    Cola asíncrona con semáforo de concurrencia.

    Uso:
        queue = RequestQueue(max_concurrent=1, max_queue=10)
        async with queue:
            response = await bridge.send(...)
    """

    def __init__(self, max_concurrent: int = 1, max_queue: int = 10, timeout: float = 300.0):
        self._sem = asyncio.Semaphore(max_concurrent)
        self._max_queue = max_queue
        self._timeout = timeout
        self._pending: int = 0
        self._total_processed: int = 0
        self._total_rejected: int = 0

    @property
    def pending(self) -> int:
        return self._pending

    @property
    def stats(self) -> dict:
        return {
            "pending": self._pending,
            "processed": self._total_processed,
            "rejected": self._total_rejected,
            "max_concurrent": self._sem._value,
        }

    async def __aenter__(self):
        if self._pending >= self._max_queue:
            self._total_rejected += 1
            raise QueueFullError(f"Cola llena ({self._pending}/{self._max_queue}). Reintenta luego.")
        self._pending += 1
        acquired = False
        try:
            acquired = await asyncio.wait_for(self._sem.acquire(), timeout=self._timeout)
        except asyncio.TimeoutError:
            self._pending -= 1
            raise QueueTimeoutError(f"Timeout esperando slot en la cola ({self._timeout}s)")
        if not acquired:
            self._pending -= 1
            raise QueueTimeoutError("No se pudo adquirir slot en la cola")
        return self

    async def __aexit__(self, *args):
        self._pending -= 1
        self._total_processed += 1
        self._sem.release()


class QueueFullError(Exception):
    """Lanzada cuando la cola está llena."""
    pass


class QueueTimeoutError(Exception):
    """Lanzada cuando se agota el timeout esperando slot."""
    pass
