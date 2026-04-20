# ----------------------------
# LLM interface
# ----------------------------
from __future__ import annotations

from typing import Any
import time

from multi_agent_workbench.llm.client_state import ClientState
from multi_agent_workbench.llm.result import LLMResult
from openai import OpenAI


class LLMClient:
    def __init__(
            self,
            model: str,
            client_state: ClientState,
    ) -> None:
        self.model = model
        # assert client_state.open_api_client is not None, "did not initialize OpenAI client"
        self._client_state = client_state

    def complete_text(self, system_prompt: str, user_prompt: str) -> LLMResult:
        assert self._client_state.open_api_client is not None, "did not initialize OpenAI client"
        return _complete_text_openai(
            model=self.model,
            client=self._client_state.open_api_client,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )


def _complete_text_openai(
    model: str,
    client: OpenAI,
    system_prompt: str,
    user_prompt: str,
) -> LLMResult:

    started = time.perf_counter()
    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    latency_ms = (time.perf_counter() - started) * 1000.0

    text = response.output_text

    usage = getattr(response, "usage", None)
    prompt_tokens = getattr(usage, "input_tokens", None) if usage else None
    completion_tokens = getattr(usage, "output_tokens", None) if usage else None
    total_tokens = getattr(usage, "total_tokens", None) if usage else None

    estimated_cost_usd = _estimate_cost_usd(
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
    )

    raw: dict[str, Any]
    try:
        raw = response.model_dump()
    except Exception:
        raw = {"response_repr": repr(response)}

    return LLMResult(
        text=text,
        model=model,
        latency_ms=latency_ms,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        estimated_cost_usd=estimated_cost_usd,
        raw=raw,
    )

def _estimate_cost_usd(
        model: str,
        prompt_tokens: int | None,
        completion_tokens: int | None,
) -> float | None:
    if prompt_tokens is None or completion_tokens is None:
        return None

    # Fill these in with the pricing model you want to track.
    # Keeping this isolated makes it easy to update later.
    pricing_per_1m = {
        "gpt-5": {"input": 0.0, "output": 0.0},
        "gpt-5-mini": {"input": 0.0, "output": 0.0},
        "gpt-4.1-mini": {"input": 0.0, "output": 0.0},
    }

    if model not in pricing_per_1m:
        return None

    price = pricing_per_1m[model]
    input_cost = (prompt_tokens / 1_000_000) * price["input"]
    output_cost = (completion_tokens / 1_000_000) * price["output"]
    return input_cost + output_cost
