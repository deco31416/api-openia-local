"""
Modelos Pydantic compatibles con la API de OpenAI.
Soporta streaming, functions, multimodal, logprobs y todos los parámetros oficiales.
"""

from typing import List, Optional, Union, Any, Literal
from pydantic import BaseModel, Field


# ── Request Models ────────────────────────────────────────

class ContentPart(BaseModel):
    """Parte de contenido multimodal (texto o imagen)."""
    type: Literal["text", "image_url"]
    text: Optional[str] = None
    image_url: Optional[dict] = None


class FunctionCall(BaseModel):
    name: str
    arguments: str


class ToolCall(BaseModel):
    id: str
    type: Literal["function"] = "function"
    function: FunctionCall


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "function", "tool"]
    content: Union[str, List[ContentPart], None] = None
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    refusal: Optional[str] = None


class ResponseFormat(BaseModel):
    type: Literal["text", "json_object", "json_schema"] = "text"
    json_schema: Optional[dict] = None


class StreamOptions(BaseModel):
    include_usage: bool = False


class ChatCompletionRequest(BaseModel):
    model: str = "gpt-4o"
    messages: List[ChatMessage]
    max_tokens: Optional[int] = None
    max_completion_tokens: Optional[int] = None
    temperature: Optional[float] = Field(default=0.7, ge=0, le=2)
    top_p: Optional[float] = Field(default=1.0, ge=0, le=1)
    n: Optional[int] = Field(default=1, ge=1)
    stream: Optional[bool] = False
    stream_options: Optional[StreamOptions] = None
    stop: Optional[Union[str, List[str]]] = None
    presence_penalty: Optional[float] = Field(default=0, ge=-2, le=2)
    frequency_penalty: Optional[float] = Field(default=0, ge=-2, le=2)
    user: Optional[str] = None
    seed: Optional[int] = None
    response_format: Optional[ResponseFormat] = None
    logprobs: Optional[bool] = None
    top_logprobs: Optional[int] = Field(default=None, ge=0, le=20)
    tools: Optional[List[dict]] = None
    tool_choice: Optional[Union[str, dict]] = None
    parallel_tool_calls: Optional[bool] = None
    # ── o3 / o4-mini: nivel de razonamiento ──
    thinking_effort: Optional[Literal["low", "medium", "high"]] = None


# ── Response Models ───────────────────────────────────────

class LogprobInfo(BaseModel):
    token: str
    logprob: float
    bytes: Optional[List[int]] = None
    top_logprobs: Optional[List[dict]] = None


class Logprobs(BaseModel):
    content: Optional[List[LogprobInfo]] = None
    refusal: Optional[List[LogprobInfo]] = None


class UsageInfo(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    prompt_tokens_details: Optional[dict] = None
    completion_tokens_details: Optional[dict] = None


class ChatChoice(BaseModel):
    index: int = 0
    message: ChatMessage
    finish_reason: Optional[Literal["stop", "length", "tool_calls", "content_filter", "function_call"]] = "stop"
    logprobs: Optional[Logprobs] = None


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatChoice]
    usage: UsageInfo
    system_fingerprint: Optional[str] = None
    service_tier: Optional[str] = None


class ChatCompletionChunk(BaseModel):
    """Chunk de streaming SSE."""
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[ChatChoice]
    usage: Optional[UsageInfo] = None
    system_fingerprint: Optional[str] = None
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
