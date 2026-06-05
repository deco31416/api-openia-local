"""
SSE Streaming — Streaming real token-por-token usando tiktoken.
Divide la respuesta en chunks y los envía via Server-Sent Events.
"""

import asyncio
import json
import time
import uuid
from typing import AsyncGenerator

from token_counter import count_tokens


class Streamer:
    """
    Genera chunks SSE compatibles con OpenAI ChatCompletionChunk.

    Uso:
        streamer = Streamer(delay_ms=30)
        async for chunk in streamer.stream(response_text, model="gpt-4o"):
            yield chunk  # SSE data
    """

    def __init__(self, delay_ms: int = 30, chunk_tokens: int = 1):
        self._delay = delay_ms / 1000.0
        self._chunk_tokens = chunk_tokens

    async def stream(
        self, text: str, model: str = "gpt-4o", stream_id: str = ""
    ) -> AsyncGenerator[str, None]:
        """
        Divide `text` en tokens con tiktoken y los emite como chunks SSE.
        Cada chunk tiene el formato OpenAI ChatCompletionChunk.
        """
        if not stream_id:
            stream_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
        created = int(time.time())

        # Tokenizar
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        tokens = enc.encode(text)

        total = len(tokens)
        role_chunk = _chunk_json(stream_id, created, model, role="assistant", content="")
        yield f"data: {role_chunk}\n\n"

        for i in range(0, total, self._chunk_tokens):
            batch = tokens[i:i + self._chunk_tokens]
            chunk_text = enc.decode(batch)
            chunk_data = _chunk_json(stream_id, created, model, content=chunk_text)
            yield f"data: {chunk_data}\n\n"
            await asyncio.sleep(self._delay)

        # Chunk final
        finish_chunk = _chunk_json(
            stream_id, created, model, content="", finish_reason="stop",
            prompt_tokens=0, completion_tokens=total,
        )
        yield f"data: {finish_chunk}\n\n"
        yield "data: [DONE]\n\n"


def _chunk_json(
    chat_id: str, created: int, model: str,
    role: str = "", content: str = "",
    finish_reason: str | None = None,
    prompt_tokens: int = 0, completion_tokens: int = 0,
) -> str:
    delta: dict = {}
    if role:
        delta["role"] = role
    if content:
        delta["content"] = content
    if not delta:
        delta = {}

    chunk: dict = {
        "id": chat_id,
        "object": "chat.completion.chunk",
        "created": created,
        "model": model,
        "choices": [{
            "index": 0,
            "delta": delta,
            "finish_reason": finish_reason,
        }],
    }
    if completion_tokens > 0:
        chunk["usage"] = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        }
    return json.dumps(chunk, ensure_ascii=False)
