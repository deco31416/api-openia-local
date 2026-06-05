"""
Graceful Shutdown — Drena requests pendientes antes de apagar.
Registra handlers de señal y trackea requests en vuelo.
"""

import asyncio
import signal
import time
from typing import Optional


class GracefulShutdown:
    """
    Maneja apagado ordenado del servidor.

    Uso:
        shutdown = GracefulShutdown(timeout=30.0)
        async with shutdown.track():
            await do_work()
        # Al recibir SIGINT/SIGTERM, espera hasta 30s a que terminen los requests.
    """

    def __init__(self, timeout: float = 30.0):
        self._timeout = timeout
        self._shutting_down = False
        self._active_requests = 0
        self._lock = asyncio.Lock()
        self._shutdown_event = asyncio.Event()

    @property
    def shutting_down(self) -> bool:
        return self._shutting_down

    @property
    def active_requests(self) -> int:
        return self._active_requests

    def track(self):
        """Context manager que trackea un request activo."""

        class _Tracker:
            def __init__(self, parent):
                self._parent = parent

            async def __aenter__(self):
                async with self._parent._lock:
                    if self._parent._shutting_down:
                        raise ShuttingDownError("Servidor en apagado — no se aceptan requests")
                    self._parent._active_requests += 1
                return self

            async def __aexit__(self, *args):
                async with self._parent._lock:
                    self._parent._active_requests -= 1
                    if self._parent._shutting_down and self._parent._active_requests == 0:
                        self._parent._shutdown_event.set()

        return _Tracker(self)

    async def wait_for_drain(self):
        """Espera a que todos los requests activos terminen (con timeout)."""
        self._shutting_down = True
        async with self._lock:
            if self._active_requests == 0:
                return
        try:
            await asyncio.wait_for(self._shutdown_event.wait(), timeout=self._timeout)
            print(f"[Shutdown] ✅ Todos los requests drenados.")
        except asyncio.TimeoutError:
            remaining = self._active_requests
            print(f"[Shutdown] ⚠️ Timeout — {remaining} requests abortados.")

    def register_signals(self):
        """Registra handlers para SIGINT y SIGTERM."""
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, lambda: asyncio.create_task(self._handle_signal()))
            except NotImplementedError:
                # Windows no soporta add_signal_handler
                pass

    async def _handle_signal(self):
        print("\n[Shutdown] ⚡ Señal recibida. Drenando requests...")
        await self.wait_for_drain()


class ShuttingDownError(Exception):
    """Lanzada cuando se rechaza un request por apagado en curso."""
    pass
