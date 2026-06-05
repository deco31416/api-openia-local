"""
Modelos Pydantic compatibles con la API de OpenAI.
"""

from typing import List, Optional, Union, Any, Literal
from pydantic import BaseModel, Field


# ── Request Models ────────────────────────────────────────

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "function", "tool"]
    content: Union[str, List[dict], None]
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    tool_calls: Optional[List[dict]] = None


class ChatCompletionRequest(BaseModel):
    model: str = "gpt-4o"
    messages: List[ChatMessage]
    max_tokens: Optional[int] = None
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: Optional[bool] = False
    stop: Optional[Union[str, List[str]]] = None
    presence_penalty: Optional[float] = 0
    frequency_penalty: Optional[float] = 0
    user: Optional[str] = None


# ── Response Models ───────────────────────────────────────

class UsageInfo(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatChoice(BaseModel):
    index: int = 0
    message: ChatMessage
    finish_reason: Optional[str] = "stop"


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatChoice]
    usage: UsageInfo


class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str = "chatgpt-web-bridge"


class ModelsListResponse(BaseModel):
    object: str = "list"
    data: List[ModelInfo]


# ── Health ────────────────────────────────────────────────

class ComponentStatus(BaseModel):
    name: str
    status: str  # "ok", "degraded", "error", "unknown"
    detail: str = ""

class HealthResponse(BaseModel):
    status: str  # "healthy", "degraded", "unhealthy"
    authenticated: bool
    bridge: str = "chatgpt-web-bridge"
    version: str = "1.7.0"
    components: list[ComponentStatus] = []
    errors: list[str] = []
    uptime_seconds: float = 0.0
