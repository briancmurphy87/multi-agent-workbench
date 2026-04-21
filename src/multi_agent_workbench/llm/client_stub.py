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

    """
    stub must return deterministic JSON for planner calls
    """
    def complete_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        if self.model == "stub-model" or self._client is None:
            lowered = user_prompt.lower()
            if any(term in lowered for term in ["what changed", "runbook", "release", "architecture"]):
                return {
                    "mode": "retrieve",
                    "needs_retrieval": True,
                    "needs_tools": False,
                    "answer_strategy": "synthesize_across_docs",
                    "rationale": "The query asks for synthesis across multiple documents.",
                }
            return {
                "mode": "answer_direct",
                "needs_retrieval": False,
                "needs_tools": False,
                "answer_strategy": "direct_response",
                "rationale": "The query appears answerable without retrieval.",
            }


def _complete_text_stub(model: str, system_prompt: str, user_prompt: str) -> LLMResult:
    started = time.perf_counter()
    lowered = user_prompt.lower()

    if "retry-demo" in lowered:
        if "instruction:" in lowered and "supported by cited evidence" in lowered:
            text = (
                "Northstar moved from a batch-first ingestion design to adding a streaming path "
                "for high-priority traffic, reducing latency to under 90 seconds [release_notes-0]. "
                "The runbook notes that if stream processor lag exceeds 5 minutes, operators should "
                "divert traffic to the batch fallback path, and memory pressure is a leading "
                "indicator of backpressure [runbook-0]."
            )
        else:
            text = (
                "Northstar added a streaming path and improved latency, but operators need to watch "
                "for lag and backpressure."
            )
    else:
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
