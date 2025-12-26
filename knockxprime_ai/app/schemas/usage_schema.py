from pydantic import BaseModel
from typing import Optional
from datetime import date
import uuid


class UsageStats(BaseModel):
    user_id: uuid.UUID
    tokens_used: int
    requests: int
    month: date
    plan_name: str
    max_tokens: int
    tokens_remaining: int
    usage_percentage: float


class MonthlyUsage(BaseModel):
    month: date
    tokens_used: int
    requests: int
    max_tokens: int
    plan_name: str


class UsageUpdate(BaseModel):
    tokens_consumed: int
    requests_increment: int = 1