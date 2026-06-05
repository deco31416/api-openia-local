"""
Lógica de prompting: escribir, enviar y esperar respuesta en ChatGPT Web.
"""

import asyncio
from typing import Optional

from css_selectors import SELECTORS


class Prompter:
    """Escribe prompts en el input de ChatGPT, los envía y espera la respuesta."""

    def __init__(self, page, timeout: int = 120_000, fast: bool = True):
        self._page = page
        self._timeout = timeout
        self._fast = fast  # Modo rápido: sin delays innecesarios

    async def send(self, text: str) -> str:
        """Envía texto a ChatGPT y devuelve respuesta completa."""
        await self._type(text)
        await self._click_send()
        return await self._wait()

    async def _type(self, text: str):
        """Escribe en el input. Modo rápido usa fill() directo sin type() lento."""
        input_el = await self._page.wait_for_selector(
            SELECTORS["prompt_input"], timeout=10_000
        )
        await input_el.click()
        if self._fast:
            # RÁPIDO: fill directo (0 delays)
            await input_el.fill(text)
        else:
            # LENTO: type carácter por carácter (simula humano)
            await input_el.fill("")
            await input_el.type(text, delay=10)

    async def _click_send(self):
        """Hace clic en enviar o Enter."""
        try:
            send = await self._page.wait_for_selector(SELECTORS["send_btn"], timeout=5_000)
            await send.click()
        except Exception:
            input_el = await self._page.query_selector(SELECTORS["prompt_input"])
            if input_el:
                await input_el.press("Enter")

    async def _wait(self, poll_ms: int = 300) -> str:
        """Espera respuesta completa. Polling rápido a 300ms (antes 800ms)."""
        # Esperar que aparezca Stop (generando)
        try:
            await self._page.wait_for_selector(SELECTORS["stop_btn"], timeout=10_000)
        except Exception:
            pass

        # Esperar que Stop desaparezca
        max_wait = self._timeout / 1000
        waited = 0.0
        while waited < max_wait:
            stop_btn = await self._page.query_selector(SELECTORS["stop_btn"])
            if stop_btn is None:
                break
            await asyncio.sleep(poll_ms / 1000)
            waited += poll_ms / 1000

        # Extraer última respuesta
        responses = await self._page.query_selector_all(SELECTORS["response_container"])
        if not responses:
            return "[Bridge] Error: no se encontró respuesta del asistente."
        return (await responses[-1].inner_text()).strip()

    async def get_conversation_id(self) -> str:
        url = self._page.url
        if "/c/" in url:
            return url.split("/c/")[-1].split("?")[0].split("#")[0]
        return ""

    async def goto_conversation(self, conversation_id: str):
        """Navega a un chat existente. Solo si no estamos ya en él."""
        current = await self.get_conversation_id()
        if current == conversation_id:
            return  # ya estamos ahí, no navegar (ahorra ~2s)
        url = f"https://chatgpt.com/c/{conversation_id}"
        await self._page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(0.5)

    async def new_conversation(self):
        """Crea nueva conversación vacía o navega a /."""
        try:
            btn = await self._page.wait_for_selector(SELECTORS["new_chat"], timeout=3_000)
            if btn:
                await btn.click()
                await asyncio.sleep(0.5)
        except Exception:
            await self._page.goto("https://chatgpt.com/")
            await asyncio.sleep(0.5)
