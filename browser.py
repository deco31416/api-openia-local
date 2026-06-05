"""
Manejo del navegador Playwright — ciclo de vida completo.
"""

import asyncio
from typing import Optional, Any

from playwright.async_api import async_playwright, Page, Browser, BrowserContext


class BrowserManager:
    """Gestiona el lanzamiento, configuración y cierre del navegador Chromium."""

    def __init__(
        self,
        headless: bool = True,
        user_data_dir: Optional[str] = None,
        chatgpt_url: str = "https://chatgpt.com/",
        timeout: int = 120_000,
    ):
        self.headless = headless
        self.user_data_dir = user_data_dir
        self.chatgpt_url = chatgpt_url
        self.timeout = timeout

        self._playwright: Any = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None

    async def start(self) -> Page:
        """Lanza Chromium y navega a ChatGPT. Devuelve la página activa."""
        self._playwright = await async_playwright().start()

        self._browser = await self._playwright.chromium.launch(
            headless=self.headless,
            channel=None,
        )

        if self.user_data_dir:
            ctx = self._browser.contexts
            self._context = ctx[0] if ctx else await self._browser.new_context()
        else:
            self._context = await self._browser.new_context(
                viewport={"width": 1440, "height": 900},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 Chrome/133.0.0.0 Safari/537.36"
                ),
            )

        self._page = await self._context.new_page()
        self._page.set_default_timeout(self.timeout)
        await self._page.goto(self.chatgpt_url, wait_until="domcontentloaded")
        await asyncio.sleep(2)
        return self._page

    async def stop(self):
        """Cierra navegador y libera recursos."""
        try:
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()
        except Exception:
            pass

    @property
    def page(self) -> Page:
        if self._page is None:
            raise RuntimeError("Browser not started. Call start() first.")
        return self._page
