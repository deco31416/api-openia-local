"""
AntiBan — Simula comportamiento humano para evitar detección.
ChatGPT detecta bots por: velocidad constante, sin pausas, sin errores de tipeo.
Este módulo inyecta variabilidad humana en cada interacción.
"""

import asyncio
import random
from typing import Optional


class AntiBan:
    """
    Simula patrones humanos: delays variables, pausas de "lectura",
    cambios de velocidad, errores ocasionales de tipeo.

    Uso:
        antiban = AntiBan(human_mode=True)
        await antiban.thinking_pause()       # "piensa" antes de escribir
        await antiban.typing_delay(len(msg)) # delay proporcional al mensaje
        await antiban.reading_pause()        # "lee" la respuesta después
    """

    def __init__(
        self,
        human_mode: bool = True,
        min_think: float = 0.5,
        max_think: float = 3.0,
        wpm: int = 60,            # palabras por minuto simuladas
    ):
        self.human_mode = human_mode
        self._min_think = min_think
        self._max_think = max_think
        self._wpm = wpm  # ~5 chars por palabra
        self._request_count: int = 0

    # ── Pausas humanas ───────────────────────────────────

    async def thinking_pause(self):
        """Simula "pensar" antes de escribir. Delay aleatorio 0.5-3s."""
        if not self.human_mode:
            return
        delay = random.uniform(self._min_think, self._max_think)
        await asyncio.sleep(delay)

    async def reading_pause(self):
        """Simula "leer" la respuesta después de recibirla. 1-4s."""
        if not self.human_mode:
            return
        delay = random.uniform(1.0, 4.0)
        await asyncio.sleep(delay)

    async def typing_delay(self, text_length: int):
        """
        Simula tiempo de tipeo humano (~60 WPM con variabilidad).
        Solo añade delay cuando human_mode=True (el fill es instantáneo,
        esta pausa simula que "escribiste" el mensaje).
        """
        if not self.human_mode:
            return
        # ~5 chars por palabra en inglés, ~4 en español
        words = max(1, text_length / 4.5)
        base_delay = (words / self._wpm) * 60  # segundos
        # ±25% variabilidad
        delay = base_delay * random.uniform(0.75, 1.25)
        # Cap: mínimo 0.2s, máximo 15s
        delay = max(0.2, min(15.0, delay))
        await asyncio.sleep(delay)

    async def inter_request_pause(self):
        """Pausa entre requests consecutivos. Más larga si van muchos seguidos."""
        if not self.human_mode:
            return
        self._request_count += 1
        # Cada 5 requests, pausa más larga (simula descanso)
        if self._request_count % 5 == 0:
            delay = random.uniform(5.0, 15.0)
            print(f"[AntiBan] ☕ Pausa larga ({delay:.0f}s) — request #{self._request_count}")
        else:
            delay = random.uniform(1.0, 3.0)
        await asyncio.sleep(delay)
