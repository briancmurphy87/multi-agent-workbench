from __future__ import annotations

from multi_agent_workbench.state.models import SupervisorDecision, WorkbenchState


class SupervisorAgent:
    name = "supervisor"

    def run(self, state: WorkbenchState) -> SupervisorDecision:
        critic_verdict = state.critic_verdict
        retrieved_count = len(state.retrieved_chunks)
        draft_answer = (state.draft_answer or "").strip()

        if critic_verdict == "retry_with_citations":
            decision = SupervisorDecision(
                action="retry_responder",
                rationale="Critic requested a revised answer with better citation support.",
                retry_instruction=(
                    "Revise the answer so every important claim is supported by cited evidence. "
                    "Use chunk ids in square brackets. Do not add unsupported claims."
                ),
            )
        elif critic_verdict == "accept_with_insufficient_evidence":
            decision = SupervisorDecision(
                action="finalize_insufficient_evidence",
                rationale="Available evidence is insufficient; finalize with a constrained answer.",
                retry_instruction=None,
            )
        elif critic_verdict == "accept" and draft_answer:
            decision = SupervisorDecision(
                action="accept",
                rationale="Critic accepted the answer and a draft is present.",
                retry_instruction=None,
            )
        elif retrieved_count == 0:
            decision = SupervisorDecision(
                action="finalize_insufficient_evidence",
                rationale="No evidence was retrieved and the system should avoid unsupported claims.",
                retry_instruction=None,
            )
        else:
            decision = SupervisorDecision(
                action="accept",
                rationale="Defaulting to accept because no retry condition was triggered.",
                retry_instruction=None,
            )

        state.supervisor_decision = decision
        return decision