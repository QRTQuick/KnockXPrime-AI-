from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid


class ChatMessage(BaseModel):
    role: str  # "user", "assistant", "system"
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = "grok-beta"
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7
    stream: Optional[bool] = False


class ChatResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]
    created: int


class UsageInfo(BaseModel):
    tokens_used: int
    tokens_remaining: int
    requests_made: int
    plan_name: str
    max_tokens: int