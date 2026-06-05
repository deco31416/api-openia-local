"""
Detección y gestión de autenticación en ChatGPT Web.
"""

import asyncio

from css_selectors import SELECTORS


class AuthManager:
    """Maneja la detección de sesión y el flujo de login manual."""

    def __init__(self, page, timeout: int = 300_000):
        self._page = page
        self._timeout = timeout
        self._authenticated = False

    async def check(self) -> bool:
        """Detecta si hay sesión activa en ChatGPT. Actualiza estado interno."""
        try:
            await self._page.wait_for_selector(
                SELECTORS["prompt_input"], timeout=10_000
            )
            print("[Auth] ✅ Sesión detectada en ChatGPT")
            self._authenticated = True
            return True
        except Exception:
            login = await self._page.query_selector(SELECTORS["login_btn"])
            if login:
                print("[Auth] ⚠️ ChatGPT pide login — inicia sesión en el navegador")
            else:
                print("[Auth] ⚠️ No se detectó sesión activa")
            self._authenticated = False
            return False

    async def ensure(self):
        """Espera hasta que el usuario se loguee manualmente (hasta 5 min)."""
        if self._authenticated:
            return
        print("[Auth] ⏳ Esperando login manual en ChatGPT...")
        try:
            await self._page.wait_for_selector(
                SELECTORS["prompt_input"], timeout=self._timeout
            )
            self._authenticated = True
            print("[Auth] ✅ Login detectado!")
        except Exception:
            raise RuntimeError("Timeout esperando login. Revisa el navegador.")

    @property
    def is_authenticated(self) -> bool:
        return self._authenticated
