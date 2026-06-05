"""
Manejo de imágenes: subida al chat y extracción de imágenes generadas.
Soporta el flujo completo imagen IN (usuario → GPT web) y OUT (GPT web → API).
"""

import asyncio
import base64
import os
import tempfile
import json
from pathlib import Path
from typing import Optional


class ImageHandler:
    """
    Maneja imágenes en ChatGPT Web:
    - Subir imágenes al input (clipboard o file input).
    - Extraer imágenes generadas por DALL-E desde el DOM.
    """

    def __init__(self, page):
        self._page = page

    # ── IMAGEN IN: usuario → ChatGPT Web ─────────────────

    async def upload_base64(self, b64_data: str, mime: str = "image/png") -> bool:
        """
        Sube una imagen en base64 al input de ChatGPT.
        Guarda temporalmente y la adjunta vía input[type=file].
        """
        try:
            # Decodificar y guardar en temp
            img_bytes = base64.b64decode(b64_data)
            suffix = ".png" if "png" in mime else ".jpg"
            fd, tmp_path = tempfile.mkstemp(suffix=suffix)
            with os.fdopen(fd, "wb") as f:
                f.write(img_bytes)

            # Adjuntar usando el input file oculto
            file_input = await self._page.query_selector('input[type="file"]')
            if file_input:
                await file_input.set_input_files(tmp_path)
                await asyncio.sleep(1.5)  # esperar upload
                print(f"[ImgIn] ✅ Imagen subida: {tmp_path}")
                return True

            print("[ImgIn] ⚠️ No se encontró input[type=file]")
            return False

        except Exception as e:
            print(f"[ImgIn] ❌ Error subiendo imagen: {e}")
            return False

    @staticmethod
    def extract_base64_from_messages(messages: list[dict]) -> list[dict]:
        """
        Extrae datos de imagen de mensajes con formato OpenAI multimodal.
        Devuelve lista de {b64, mime} encontrados.
        """
        images: list[dict] = []
        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, list):
                for part in content:
                    if isinstance(part, dict) and part.get("type") == "image_url":
                        url = part.get("image_url", {}).get("url", "")
                        if url.startswith("data:"):
                            # Formato: data:image/png;base64,XXXX
                            header, b64 = url.split(",", 1)
                            mime = header.replace("data:", "").replace(";base64", "")
                            images.append({"b64": b64, "mime": mime})
        return images

    # ── IMAGEN OUT: ChatGPT Web → API ────────────────────

    async def extract_generated(self) -> list[str]:
        """
        Extrae URLs de imágenes generadas por DALL-E en la última respuesta.
        """
        urls: list[str] = []
        try:
            from css_selectors import SELECTORS

            imgs = await self._page.query_selector_all(
                SELECTORS["generated_image"]
            )
            last_msgs = await self._page.query_selector_all(
                SELECTORS["response_container"]
            )
            if last_msgs:
                imgs = await last_msgs[-1].query_selector_all("img")
            for img in imgs:
                src = await img.get_attribute("src")
                if src and ("oaidalleapiprodscus" in src or "files." in src):
                    urls.append(src)
        except Exception as e:
            print(f"[ImgOut] ⚠️ Error extrayendo imágenes: {e}")
        return urls
