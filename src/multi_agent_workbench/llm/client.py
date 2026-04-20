# ----------------------------
# LLM interface
# ----------------------------
from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import time


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


class LLMClient:
    def __init__(self, model: str) -> None:
        self.model = model

    def complete_text(self, system_prompt: str, user_prompt: str) -> LLMResult:
        # Replace this stub by adapting your existing llm.py wrapper.
        started = time.perf_counter()
        text = (
            "STUB_RESPONSE\n\n"
            f"System prompt: {system_prompt[:120]}...\n"
            f"User prompt: {user_prompt[:240]}..."
        )
        latency_ms = (time.perf_counter() - started) * 1000.0
        return LLMResult(text=text, model=self.model, latency_ms=latency_ms)