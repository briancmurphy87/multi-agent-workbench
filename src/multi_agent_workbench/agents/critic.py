from __future__ import annotations

from multi_agent_workbench.state.models import WorkbenchState


class CriticAgent:
    name = "critic"

    def run(self, state: WorkbenchState) -> str:
        answer = state.draft_answer or ""
        has_citation = "[" in answer and "]" in answer
        has_evidence = len(state.retrieved_chunks) > 0

        if has_evidence and has_citation:
            verdict = "accept"
        elif has_evidence and not has_citation:
            verdict = "retry_with_citations"
        else:
            verdict = "accept_with_insufficient_evidence"

        state.critic_verdict = verdict
        return verdict