from __future__ import annotations

import time

from multi_agent_workbench.llm.client import LLMClient
from multi_agent_workbench.llm.client_state import ClientState
from multi_agent_workbench.llm.result import LLMResult


class LLMClientStub(LLMClient):
    def __init__(self, api_key: str | None = None) -> None:
        super().__init__(model="stub-model", client_state=ClientState(open_api_client=None))

    def complete_text(self, system_prompt: str, user_prompt: str) -> LLMResult:
        return _complete_text_stub(
            model=self.model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

def _complete_text_stub(model: str, system_prompt: str, user_prompt: str) -> LLMResult:
    started = time.perf_counter()
    text = (
        "STUB_RESPONSE\n\n"
        f"System prompt: {system_prompt[:120]}...\n"
        f"User prompt: {user_prompt[:240]}..."
    )
    latency_ms = (time.perf_counter() - started) * 1000.0
    return LLMResult(
        text=text,
        model=model,
        latency_ms=latency_ms,
        prompt_tokens=None,
        completion_tokens=None,
        total_tokens=None,
        estimated_cost_usd=None,
        raw={"stub": True},
    )
