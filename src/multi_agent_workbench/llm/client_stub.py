from __future__ import annotations

import time
from typing import Any

from multi_agent_workbench.llm.client_base import LLMClientABC
from multi_agent_workbench.llm.result import LLMResult


class LLMClientStub(LLMClientABC):
    def __init__(self, api_key: str | None = None) -> None:
        super().__init__(model="stub-model")

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
        # if self.model == "stub-model" or self._client is None:
        lowered = user_prompt.lower()
        if any(
                term in lowered
                for term in [
                    "what changed",
                    "release",
                    "architecture",
                    "runbook",
                    "sqlite",
                    "wal",
                    "locking",
                    "transaction",
                    "rollback",
                    "journal",
                    "checkpoint",
                    "concurrency",
                    "caveat",
                    "tradeoff",
                    "changes",
                ]
        ):
            return {
                "mode": "retrieve",
                "needs_retrieval": True,
                "needs_tools": False,
                "answer_strategy": "synthesize_across_docs",
                "rationale": "The query asks for information that should be grounded in retrieved documents.",
            }

        else:
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
    elif "sqlite" in lowered:
        if "which engineer originally approved wal mode" in lowered:
            text = (
                "I do not have enough evidence in the retrieved documents to determine "
                "which engineer originally approved WAL mode for release in SQLite."
            )
        elif "wal mode" in lowered and "caveat" in lowered:
            text = (
                "SQLite documents several WAL-mode caveats, including shared-memory "
                "requirements, constraints around network filesystems, checkpointing, "
                "and compatibility considerations [wal_mode-47]."
            )
        elif "concurrency" in lowered and "locking" in lowered:
            text = (
                "SQLite describes rollback-mode locking separately from WAL-mode "
                "behavior. The locking documentation explains SQLite version 3 locking, "
                "while the WAL documentation describes how readers and writers interact "
                "through the WAL and wal-index [locking-0] [wal_mode-43]."
            )
        elif "tradeoffs" in lowered and "rollback" in lowered:
            text = (
                "SQLite describes WAL as adding checkpointing to the traditional read/write "
                "rollback-journal model. WAL can improve write performance and concurrency, "
                "but introduces checkpointing and WAL file management tradeoffs [wal_mode-7] [wal_mode-15]."
            )
        elif "recent sqlite releases" in lowered or "recent sqlite" in lowered:
            text = (
                "Recent SQLite documentation notes WAL-related bug fixes and query behavior "
                "changes, including the WAL-reset bug discussion and recent release notes [wal_mode-48]."
            )
        else:
            text = "SQLite answer synthesized from retrieved evidence [wal_mode-0]."
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
