"""
ChatGPT Web Bridge — Orquestador principal.
Coordina browser, auth, prompting, modelos e imágenes.
"""

import asyncio
from typing import Optional

from browser import BrowserManager
from auth import AuthManager
from prompter import Prompter
from model_manager import ModelManager
from image_handler import ImageHandler


class ChatGPTBridge:
    """
    Bridge que controla ChatGPT Web via Playwright.
    Delega cada responsabilidad a un módulo especializado.

    Uso:
        bridge = await ChatGPTBridge(headless=False).start()
        response, model, images = await bridge.send("Hola", model="gpt-4o")
        await bridge.stop()
    """

    def __init__(
        self,
        headless: bool = True,
        chatgpt_url: str = "https://chatgpt.com/",
        timeout: int = 120_000,
    ):
        self._browser = BrowserManager(
            headless=headless, chatgpt_url=chatgpt_url, timeout=timeout
        )
        self._auth: Optional[AuthManager] = None
        self._prompter: Optional[Prompter] = None
        self._models: Optional[ModelManager] = None
        self._images: Optional[ImageHandler] = None

    # ── Lifecycle ────────────────────────────────────────

    async def start(self) -> "ChatGPTBridge":
        page = await self._browser.start()
        self._auth = AuthManager(page)
        self._prompter = Prompter(page, timeout=self._browser.timeout)
        self._models = ModelManager(page)
        self._images = ImageHandler(page)
        await self._auth.check()
        return self

    async def stop(self):
        await self._browser.stop()

    async def __aenter__(self):
        return await self.start()

    async def __aexit__(self, *args):
        await self.stop()

    # ── API pública ──────────────────────────────────────

    async def send(
        self,
        text: str,
        model: str = "",
        images: list[dict] | None = None,
        new_chat: bool = False,
    ) -> tuple[str, str, list[str]]:
        """
        Envía prompt + imágenes opcionales a ChatGPT Web.

        Args:
            text: Prompt de texto.
            model: Modelo deseado (cambia automáticamente si difiere).
            images: Lista de {"b64": "...", "mime": "image/..."} opcional.
            new_chat: Si True, crea nueva conversación.

        Returns:
            (respuesta_texto, modelo_real_usado, urls_imagenes_generadas)
        """
        if not self._auth.is_authenticated:
            await self._auth.ensure()

        if new_chat:
            await self._prompter.new_conversation()

        # Subir imágenes si vienen
        if images:
            for img in images:
                await self._images.upload_base64(
                    img["b64"], img.get("mime", "image/png")
                )

        # Cambiar modelo si se pide
        actual = await self._models.current()
        if model and model.lower() not in actual.lower():
            ok = await self._models.switch(model)
            actual = model if ok else actual
            tag = "🔄" if ok else "⚠️"
            print(f"[Bridge] {tag} Modelo: {actual}")

        response = await self._prompter.send(text)
        generated = await self._images.extract_generated()
        return response, actual, generated

    @property
    def is_authenticated(self) -> bool:
        return self._auth.is_authenticated if self._auth else False


# ── Singleton ────────────────────────────────────────────

_bridge_instance: Optional[ChatGPTBridge] = None
_lock = asyncio.Lock()


async def get_bridge(headless: bool = True) -> ChatGPTBridge:
    global _bridge_instance
    async with _lock:
        if _bridge_instance is None:
            _bridge_instance = await ChatGPTBridge(headless=headless).start()
        return _bridge_instance
