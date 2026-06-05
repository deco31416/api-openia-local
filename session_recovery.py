"""
Session Recovery — Recupera sesiones de ChatGPT tras caídas o expiración.
Guarda cookies, detecta sesiones muertas y restaura automáticamente.
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Optional


class SessionRecovery:
    """
    Persiste y recupera sesiones de ChatGPT.

    Uso:
        sr = SessionRecovery(context)
        await sr.save()           # guarda cookies
        ok = await sr.restore()   # restaura sesión guardada
    """

    def __init__(self, context, filepath: str = "session.json"):
        self._context = context
        self._path = Path(filepath)
        self._last_saved: float = 0

    async def save(self):
        """Guarda cookies y localStorage de la sesión actual."""
        try:
            cookies = await self._context.cookies()
            self._path.write_text(
                json.dumps({"cookies": cookies, "saved_at": asyncio.get_event_loop().time()}),
                "utf-8",
            )
            self._last_saved = asyncio.get_event_loop().time()
            print("[Session] 💾 Cookies guardadas")
        except Exception as e:
            print(f"[Session] ⚠️ Error guardando cookies: {e}")

    async def restore(self) -> bool:
        """Intenta restaurar cookies desde disco. Retorna True si hay datos."""
        if not self._path.exists():
            return False
        try:
            data = json.loads(self._path.read_text("utf-8"))
            cookies = data.get("cookies", [])
            if cookies:
                await self._context.add_cookies(cookies)
                print(f"[Session] ✅ {len(cookies)} cookies restauradas")
                return True
        except Exception as e:
            print(f"[Session] ⚠️ Error restaurando cookies: {e}")
        return False

    async def ensure_valid(self, page, timeout: int = 10) -> bool:
        """Verifica si la sesión restaurada sigue siendo válida."""
        try:
            from css_selectors import SELECTORS
            await page.goto("https://chatgpt.com/", wait_until="domcontentloaded")
            await page.wait_for_selector(SELECTORS["prompt_input"], timeout=timeout * 1000)
            print("[Session] ✅ Sesión válida detectada")
            return True
        except Exception:
            print("[Session] ⚠️ Sesión inválida o expirada")
            return False
