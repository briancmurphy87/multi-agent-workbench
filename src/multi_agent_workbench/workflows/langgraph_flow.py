from __future__ import annotations

from langgraph.graph import END, StateGraph

from multi_agent_workbench.agents.critic import CriticAgent
from multi_agent_workbench.agents.planner import PlannerAgent
from multi_agent_workbench.agents.responder import ResponderAgent
from multi_agent_workbench.agents.retriever import RetrieverAgent
from multi_agent_workbench.agents.supervisor import SupervisorAgent
from multi_agent_workbench.observability.traces import traced_agent_step
from multi_agent_workbench.state.models import WorkbenchState


def route_after_plan(state: WorkbenchState) -> str:
    if state.planner_decision is not None and state.planner_decision.needs_retrieval:
        return "retrieve"
    return "respond"


def route_after_supervisor(state: WorkbenchState) -> str:
    if (
        state.supervisor_decision is not None
        and state.supervisor_decision.action == "retry_responder"
        and state.retry_count < 1
    ):
        return "respond_retry"
    return "finalize"


class LangGraphWorkflow:
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

        # init langgraph
        builder = StateGraph(WorkbenchState)

        builder.add_node("plan", self.plan_node)
        builder.add_node("retrieve", self.retrieve_node)
        builder.add_node("respond", self.respond_node)
        builder.add_node("critic", self.critique_node)
        builder.add_node("supervisor", self.supervise_node)
        builder.add_node("respond_retry", self.respond_retry_node)
        builder.add_node("critic_retry", self.critique_retry_node)
        builder.add_node("finalize", self.finalize_node)

        builder.set_entry_point("plan")

        builder.add_conditional_edges(
            "plan",
            route_after_plan,
            {
                "retrieve": "retrieve",
                "respond": "respond",
            },
        )

        builder.add_edge("retrieve", "respond")
        builder.add_edge("respond", "critic")
        builder.add_edge("critic", "supervisor")

        builder.add_conditional_edges(
            "supervisor",
            route_after_supervisor,
            {
                "respond_retry": "respond_retry",
                "finalize": "finalize",
            },
        )

        builder.add_edge("respond_retry", "critic_retry")
        builder.add_edge("critic_retry", "supervisor")
        builder.add_edge("finalize", END)

        self.graph = builder.compile()

    def run(self, state: WorkbenchState) -> WorkbenchState:
        result = self.graph.invoke(state)
        if isinstance(result, WorkbenchState):
            return result
        return WorkbenchState.model_validate(result)

    def plan_node(self, state: WorkbenchState) -> WorkbenchState:
        with traced_agent_step(
                state, self.planner.name, "plan", state.user_query
        ) as step:
            decision = self.planner.run(state)
            step["output_summary"] = (
                f"mode={decision.mode}; "
                f"needs_retrieval={decision.needs_retrieval}; "
                f"needs_tools={decision.needs_tools}; "
                f"strategy={decision.answer_strategy}"
            )
            state.artifacts["planner"] = {
                "mode": decision.mode,
                "needs_retrieval": decision.needs_retrieval,
                "needs_tools": decision.needs_tools,
                "answer_strategy": decision.answer_strategy,
                "rationale": decision.rationale,
            }
        return state

    def retrieve_node(self, state: WorkbenchState) -> WorkbenchState:
        with traced_agent_step(
                state,
                self.retriever.name,
                "retrieve",
                state.user_query
        ) as step:
            self.retriever.run(state)
            step["output_summary"] = f"retrieved={len(state.retrieved_chunks)}"
        return state

    def respond_node(self, state: WorkbenchState) -> WorkbenchState:
        with traced_agent_step(
                state,
                self.responder.name,
                "respond",
                state.user_query
        ) as step:
            self.responder.run(state)
            step["output_summary"] = (state.draft_answer or "")[:160]
        return state

    def critique_node(self, state: WorkbenchState) -> WorkbenchState:
        with traced_agent_step(
                state, self.critic.name, "critique", state.user_query
        ) as step:
            verdict = self.critic.run(state)
            step["output_summary"] = verdict
        return state

    def supervise_node(self, state: WorkbenchState) -> WorkbenchState:
        with traced_agent_step(
                state, self.supervisor.name, "supervise", state.user_query
        ) as step:
            decision = self.supervisor.run(state)
            state.supervisor_decision = decision
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
        return state

    def respond_retry_node(self, state: WorkbenchState) -> WorkbenchState:
        instruction = (
            state.supervisor_decision.retry_instruction
            if state.supervisor_decision is not None
            else None
        )
        with traced_agent_step(state, self.responder.name, "respond_retry", state.user_query) as step:
            self.responder.run(state, revision_instruction=instruction)
            step["output_summary"] = "retried_with_supervisor_instruction"
            state.retry_count += 1
        return state

    def critique_retry_node(self, state: WorkbenchState) -> WorkbenchState:
        with traced_agent_step(state, self.critic.name, "critique_retry", state.user_query) as step:
            verdict = self.critic.run(state)
            step["output_summary"] = verdict
        return state

    def finalize_node(self, state: WorkbenchState) -> WorkbenchState:
        if (
            state.supervisor_decision is not None
            and state.supervisor_decision.action == "finalize_insufficient_evidence"
        ):
            state.final_answer = (
                state.draft_answer
                or "I do not have enough evidence in the retrieved documents to answer confidently."
            )
        else:
            state.final_answer = state.draft_answer
        return state