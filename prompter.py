"""
Lógica de prompting: escribir, enviar y esperar respuesta en ChatGPT Web.
"""

import asyncio
from typing import Optional

from css_selectors import SELECTORS


class Prompter:
    """Escribe prompts en el input de ChatGPT, los envía y espera la respuesta."""

    def __init__(self, page, timeout: int = 120_000):
        self._page = page
        self._timeout = timeout

    async def send(self, text: str) -> str:
        """Envía un texto a ChatGPT y devuelve la respuesta completa."""
        await self._type(text)
        await self._click_send()
        return await self._wait()

    async def _type(self, text: str):
        """Escribe el prompt en el campo de entrada."""
        input_el = await self._page.wait_for_selector(
            SELECTORS["prompt_input"], timeout=10_000
        )
        await input_el.click()
        await asyncio.sleep(0.3)
        await input_el.fill("")
        await input_el.type(text, delay=10)
        await asyncio.sleep(0.3)

    async def _click_send(self):
        """Hace clic en enviar o presiona Enter."""
        try:
            send = await self._page.wait_for_selector(
                SELECTORS["send_btn"], timeout=5_000
            )
            await send.click()
        except Exception:
            input_el = await self._page.query_selector(SELECTORS["prompt_input"])
            if input_el:
                await input_el.press("Enter")

    async def _wait(self, poll_ms: int = 800) -> str:
        """Espera a que la respuesta termine (stop button desaparece)."""
        await asyncio.sleep(1)

        # Esperar que aparezca "Stop" (indica generación en curso)
        try:
            await self._page.wait_for_selector(SELECTORS["stop_btn"], timeout=10_000)
        except Exception:
            pass

        # Esperar que "Stop" desaparezca (terminó)
        max_wait = self._timeout / 1000
        waited = 0.0
        while waited < max_wait:
            stop_btn = await self._page.query_selector(SELECTORS["stop_btn"])
            if stop_btn is None:
                break
            await asyncio.sleep(poll_ms / 1000)
            waited += poll_ms / 1000

        await asyncio.sleep(0.5)

        # Extraer última respuesta
        responses = await self._page.query_selector_all(
            SELECTORS["response_container"]
        )
        if not responses:
            return "[Bridge] Error: no se encontró respuesta del asistente."
        return (await responses[-1].inner_text()).strip()

    async def new_conversation(self):
        """Intenta crear una nueva conversación vacía."""
        try:
            btn = await self._page.wait_for_selector(
                SELECTORS["new_chat"], timeout=5_000
            )
            if btn:
                await btn.click()
                await asyncio.sleep(2)
        except Exception:
            await self._page.goto(self._page.url)
            await asyncio.sleep(2)
