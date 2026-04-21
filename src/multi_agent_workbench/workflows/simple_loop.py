from __future__ import annotations

from multi_agent_workbench.agents.critic import CriticAgent
from multi_agent_workbench.agents.planner import PlannerAgent
from multi_agent_workbench.agents.responder import ResponderAgent
from multi_agent_workbench.agents.retriever import RetrieverAgent
from multi_agent_workbench.agents.supervisor import SupervisorAgent
from multi_agent_workbench.observability.traces import traced_agent_step
from multi_agent_workbench.state.models import WorkbenchState


class SimpleWorkflow:
    def __init__(
            self,
            planner: PlannerAgent,
            retriever: RetrieverAgent,
            responder: ResponderAgent,
            critic: CriticAgent,
            supervisor: SupervisorAgent,
    ) -> None:
        self.planner = planner
        self.retriever = retriever
        self.responder = responder
        self.critic = critic
        self.supervisor = supervisor

    def run(self, state: WorkbenchState) -> WorkbenchState:
        # agent = planner -> proposes a path
        with traced_agent_step(state, self.planner.name, "plan", state.user_query) as step:
            decision = self.planner.run(state)
            # store rationale
            step["output_summary"] = (
                f"mode={decision.mode}; "
                f"needs_retrieval={decision.needs_retrieval}; "
                f"needs_tools={decision.needs_tools}; "
                f"strategy={decision.answer_strategy}"
            )
            # store planner artifacts
            state.artifacts["planner"] = {
                "mode": decision.mode,
                "needs_retrieval": decision.needs_retrieval,
                "needs_tools": decision.needs_tools,
                "answer_strategy": decision.answer_strategy,
                "rationale": decision.rationale,
            }

        # agent = retrieval (optional)
        if decision.needs_retrieval:
            with traced_agent_step(state, self.retriever.name, "retrieve", state.user_query) as step:
                self.retriever.run(state)
                step["output_summary"] = f"retrieved={len(state.retrieved_chunks)}"

        # agent = responder
        with traced_agent_step(state, self.responder.name, "respond", state.user_query) as step:
            self.responder.run(state)
            step["output_summary"] = (state.draft_answer or "")[:160]

        # agent = critic -> assesses output quality
        with traced_agent_step(state, self.critic.name, "critique", state.user_query) as step:
            verdict = self.critic.run(state)
            step["output_summary"] = verdict

        # agent = supervisor -> decides next action
        with traced_agent_step(state, self.supervisor.name, "supervise", state.user_query) as step:
            supervisor_decision = self.supervisor.run(state)
            step["output_summary"] = (
                f"action={supervisor_decision.action}; "
                f"rationale={supervisor_decision.rationale[:120]}"
            )
            # handle 'agent = supervisor' action
            state = _handle_supervisor_action(
                supervisor_decision=supervisor_decision,
                state=state,
                responder=self.responder,
                critic=self.critic,
            )
            # store supervisor artifacts
            state.artifacts["supervisor"] = {
                "action": supervisor_decision.action,
                "rationale": supervisor_decision.rationale,
                "retry_instruction": supervisor_decision.retry_instruction,
            }

        # finalize
        state.final_answer = state.draft_answer
        return state


def _handle_supervisor_action(
    supervisor_decision: SupervisorDecision,
    state: WorkbenchState,
    responder: ResponderAgent,
    critic: CriticAgent,
) -> WorkbenchState:
    if supervisor_decision.action == "retry_responder":
        with traced_agent_step(
                state,
                responder.name,
                "respond_retry",
                state.user_query
        ) as step:
            responder.run(
                state,
                revision_instruction=supervisor_decision.retry_instruction,
            )
            step["output_summary"] = "retried_with_supervisor_instruction"

        with traced_agent_step(state, critic.name, "critique_retry", state.user_query) as step:
            verdict = critic.run(state)
            step["output_summary"] = verdict

        state.final_answer = state.draft_answer

    elif supervisor_decision.action == "finalize_insufficient_evidence":
        state.final_answer = (
                state.draft_answer
                or "I do not have enough evidence in the retrieved documents to answer confidently."
        )

    else:
        state.final_answer = state.draft_answer

    return state