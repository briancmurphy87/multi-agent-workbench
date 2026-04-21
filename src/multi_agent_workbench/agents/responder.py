from __future__ import annotations

from multi_agent_workbench.llm.client_base import LLMClientABC
from multi_agent_workbench.state.models import WorkbenchState


class ResponderAgent:
    name = "responder"

    def __init__(self, llm: LLMClientABC) -> None:
        self.llm = llm

    def run(self, state: WorkbenchState, revision_instruction: str | None = None) -> str:
        evidence = "\n\n".join(
            f"[{c.chunk_id}] {c.text[:900]}" for c in state.retrieved_chunks
        ) or "No retrieved evidence."

        system_prompt = (
            "You are a careful research assistant. Answer only from provided evidence. "
            "If evidence is insufficient, say so. Include citations using chunk ids in square brackets."
        )

        extra_instruction = revision_instruction or "Write a concise answer with citations."
        user_prompt = (
            f"Question:\n{state.user_query}\n\n"
            f"Evidence:\n{evidence}\n\n"
            f"Instruction:\n{extra_instruction}"
        )
        result = self.llm.complete_text(system_prompt=system_prompt, user_prompt=user_prompt)
        state.draft_answer = result.text
        state.artifacts["responder_metrics"] = {
            "latency_ms": result.latency_ms,
            "prompt_tokens": result.prompt_tokens,
            "completion_tokens": result.completion_tokens,
            "total_tokens": result.total_tokens,
            "estimated_cost_usd": result.estimated_cost_usd,
            "model": result.model,
        }
        return result.text