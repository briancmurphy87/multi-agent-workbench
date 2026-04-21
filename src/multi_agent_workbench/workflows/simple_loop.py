from __future__ import annotations

from multi_agent_workbench.agents.critic import CriticAgent
from multi_agent_workbench.agents.planner import PlannerAgent
from multi_agent_workbench.agents.planner_models import PlannerDecision
from multi_agent_workbench.agents.responder import ResponderAgent
from multi_agent_workbench.agents.retriever import RetrieverAgent
from multi_agent_workbench.agents.supervisor import SupervisorAgent
from multi_agent_workbench.observability.traces import traced_agent_step
from multi_agent_workbench.state.models import WorkbenchState, SupervisorDecision


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
        _plan(state=state, planner=self.planner)

        # agent = retrieval (optional)
        _retrieve(
            state=state,
            retriever=self.retriever,
        )

        # agent = responder
        _respond(state=state, responder=self.responder)

        # agent = critic -> assesses output quality
        _critique(state=state, critic=self.critic)

        # agent = supervisor -> decides next action
        _supervise(
            state=state,
            supervisor=self.supervisor,
        )
        # handle 'agent = supervisor' action
        if state.supervisor_decision.action == "retry_responder":
            _respond_retry(
                state=state,
                responder=self.responder,
            )
            _critique_retry(
                state=state,
                critic=self.critic,
            )
            # store supervisor artifacts
            state.artifacts["supervisor"] = {
                "action": state.supervisor_decision.action,
                "rationale": state.supervisor_decision.rationale,
                "retry_instruction": state.supervisor_decision.retry_instruction,
            }

        # finalize draft from this run
        _finalize(state=state)
        return state


def _plan(
    state: WorkbenchState,
    planner: PlannerAgent,
) -> None:
    with traced_agent_step(
            state,
            planner.name,
            "plan",
            state.user_query
    ) as step:

        decision = planner.run(state)
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
        state.planner_decision = decision

def _retrieve(
    state: WorkbenchState,
    retriever: RetrieverAgent,
) -> None:
    if state.planner_decision is None or not state.planner_decision.needs_retrieval:
        return

    with traced_agent_step(
            state,
            retriever.name,
            "retrieve",
            state.user_query
    ) as step:

        retriever.run(state)
        step["output_summary"] = f"retrieved={len(state.retrieved_chunks)}"

def _respond(
    state: WorkbenchState,
    responder: ResponderAgent,
) -> None:
    with traced_agent_step(
            state,
            responder.name,
            "respond",
            state.user_query
    ) as step:
        responder.run(state)
        step["output_summary"] = (state.draft_answer or "")[:160]


def _critique(
    state: WorkbenchState,
    critic: CriticAgent,
) -> None:
    with traced_agent_step(state, critic.name, "critique", state.user_query) as step:
        verdict = critic.run(state)
        step["output_summary"] = verdict


def _supervise(
    state: WorkbenchState,
    supervisor: SupervisorAgent,
) -> None:
    with traced_agent_step(state, supervisor.name, "supervise", state.user_query) as step:
        state.supervisor_decision = supervisor.run(state)
        step["output_summary"] = (
            f"action={state.supervisor_decision.action}; "
            f"rationale={state.supervisor_decision.rationale[:120]}"
        )


def _respond_retry(
    state: WorkbenchState,
    responder: ResponderAgent,
) -> None:

    with traced_agent_step(
            state,
            responder.name,
            "respond_retry",
            state.user_query
    ) as step:
        responder.run(
            state,
            revision_instruction=state.supervisor_decision.retry_instruction,
        )
        step["output_summary"] = "retried_with_supervisor_instruction"
        state.retry_count += 1


def _critique_retry(
    state: WorkbenchState,
    critic: CriticAgent,
) -> None:
    with traced_agent_step(
            state,
            critic.name, "critique_retry", state.user_query) as step:
        verdict = critic.run(state)
        step["output_summary"] = verdict

def _finalize(state: WorkbenchState) -> None:
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