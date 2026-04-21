from __future__ import annotations

from multi_agent_workbench.agents.critic import CriticAgent
from multi_agent_workbench.agents.planner import PlannerAgent
from multi_agent_workbench.agents.responder import ResponderAgent
from multi_agent_workbench.agents.retriever import RetrieverAgent
from multi_agent_workbench.observability.traces import traced_agent_step
from multi_agent_workbench.state.models import WorkbenchState


class SimpleWorkflow:
    def __init__(
        self,
        planner: PlannerAgent,
        retriever: RetrieverAgent,
        responder: ResponderAgent,
        critic: CriticAgent,
    ) -> None:
        self.planner = planner
        self.retriever = retriever
        self.responder = responder
        self.critic = critic

    def run(self, state: WorkbenchState) -> WorkbenchState:
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

        if decision.needs_retrieval:
            with traced_agent_step(state, self.retriever.name, "retrieve", state.user_query) as step:
                self.retriever.run(state)
                step["output_summary"] = f"retrieved={len(state.retrieved_chunks)}"

        with traced_agent_step(state, self.responder.name, "respond", state.user_query) as step:
            self.responder.run(state)
            step["output_summary"] = (state.draft_answer or "")[:160]

        with traced_agent_step(state, self.critic.name, "critique", state.user_query) as step:
            verdict = self.critic.run(state)
            step["output_summary"] = verdict

        if verdict == "retry_with_citations":
            with traced_agent_step(state, self.responder.name, "respond_retry", state.user_query) as step:
                retry_prefix = "Revise the prior answer to ensure every claim is supported by cited evidence.\n\n"
                state.user_query = retry_prefix + state.user_query
                self.responder.run(state)
                step["output_summary"] = "retried_with_citations"

        state.final_answer = state.draft_answer
        return state