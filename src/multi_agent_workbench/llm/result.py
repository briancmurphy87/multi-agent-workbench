from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class LLMResult:
    text: str
    model: str
    latency_ms: float
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    estimated_cost_usd: float | None = None
    raw: dict[str, Any] | None = None
