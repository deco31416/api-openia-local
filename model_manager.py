"""
Detección y cambio de modelo en ChatGPT Web.
"""

import asyncio

from css_selectors import SELECTORS, resolve_model_name


class ModelManager:
    """Lee el modelo activo en ChatGPT web y permite cambiarlo programáticamente."""

    def __init__(self, page):
        self._page = page

    async def current(self) -> str:
        """Lee el nombre del modelo seleccionado actualmente."""
        try:
            el = await self._page.query_selector(SELECTORS["current_model"])
            if el:
                text = await el.inner_text()
                return text.strip() or "gpt-4o"
        except Exception:
            pass

        try:
            btn = await self._page.query_selector(SELECTORS["model_selector"])
            if btn:
                label = await btn.get_attribute("aria-label")
                if label:
                    return label.replace("Model", "").strip() or "gpt-4o"
        except Exception:
            pass

        return "gpt-4o"

    async def switch(self, model_name: str) -> bool:
        """
        Cambia al modelo indicado usando el dropdown de ChatGPT.
        Prueba el nombre exacto y luego los fallbacks conocidos.
        """
        try:
            selector = await self._page.wait_for_selector(
                SELECTORS["model_selector"], timeout=5_000
            )
            if selector:
                await selector.click()
                await asyncio.sleep(0.8)
        except Exception:
            return False

        found = await self._try_select(resolve_model_name(model_name))
        if not found:
            try:
                await self._page.keyboard.press("Escape")
            except Exception:
                pass
        return found

    async def _try_select(self, names: list[str]) -> bool:
        """Intenta hacer clic en cada nombre candidato del dropdown."""
        for name in names:
            try:
                opt = await self._page.wait_for_selector(
                    SELECTORS["model_option_tmpl"].format(model=name),
                    timeout=2_000,
                )
                if opt:
                    await opt.click()
                    await asyncio.sleep(1.0)
                    return True
            except Exception:
                continue
        return False
