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
        self._plan(state=state)

        # agent = retrieval (optional)
        self._retrieve(state=state)

        # agent = responder
        self._respond(state=state)

        # agent = critic -> assesses output quality
        self._critique(state=state)

        # agent = supervisor -> decides next action
        self._supervise(state=state)

        # handle 'agent = supervisor' action (iteratively)
        while (
                state.supervisor_decision is not None
                and state.supervisor_decision.action == "retry_responder"
                and state.retry_count < 1
        ):
            self._respond_retry(state=state)
            self._critique_retry(state=state)
            self._supervise(state=state)

        # finalize draft from this run
        self._finalize(state=state)
        return state


    def _plan(
        self,
        state: WorkbenchState,
    ) -> None:
        with traced_agent_step(
                state,
                self.planner.name,
                "plan",
                state.user_query
        ) as step:

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

    def _retrieve(
        self,
        state: WorkbenchState,
    ) -> None:
        if state.planner_decision is None or not state.planner_decision.needs_retrieval:
            return

        with traced_agent_step(
                state,
                self.retriever.name,
                "retrieve",
                state.user_query
        ) as step:

            self.retriever.run(state)
            step["output_summary"] = f"retrieved={len(state.retrieved_chunks)}"

    def _respond(
        self,
        state: WorkbenchState,
    ) -> None:
        with traced_agent_step(
                state,
                self.responder.name,
                "respond",
                state.user_query
        ) as step:
            self.responder.run(state)
            step["output_summary"] = (state.draft_answer or "")[:160]

    def _critique(
        self,
        state: WorkbenchState,
    ) -> None:
        with traced_agent_step(
                state, self.critic.name, "critique", state.user_query
        ) as step:
            verdict = self.critic.run(state)
            step["output_summary"] = verdict

    def _supervise(
        self,
        state: WorkbenchState,
    ) -> None:
        with traced_agent_step(
                state, self.supervisor.name, "supervise", state.user_query
        ) as step:
            decision = self.supervisor.run(state)
            step["output_summary"] = (
                f"action={decision.action}; "
                f"rationale={decision.rationale[:120]}"
            )

            # store supervisor artifacts
            state.artifacts["supervisor"] = {
                "action": decision.action,
                "rationale": decision.rationale,
                "retry_instruction": decision.retry_instruction,
            }

            state.supervisor_decision = decision

    def _respond_retry(
        self,
        state: WorkbenchState,
    ) -> None:

        with traced_agent_step(
                state,
                self.responder.name,
                "respond_retry",
                state.user_query
        ) as step:
            self.responder.run(
                state,
                revision_instruction=state.supervisor_decision.retry_instruction,
            )
            step["output_summary"] = "retried_with_supervisor_instruction"
            state.retry_count += 1

    def _critique_retry(
        self,
        state: WorkbenchState,
    ) -> None:
        with traced_agent_step(
                state,
                self.critic.name,
                "critique_retry",
                state.user_query
        ) as step:
            verdict = self.critic.run(state)
            step["output_summary"] = verdict

    def _finalize(self, state: WorkbenchState) -> None:
        if state.supervisor_decision is None:
            state.final_answer = state.draft_answer
            return

        if state.supervisor_decision.action == "finalize_insufficient_evidence":
            state.final_answer = (
                state.draft_answer
                or "I do not have enough evidence in the retrieved documents to answer confidently."
            )
        else:
            state.final_answer = state.draft_answer