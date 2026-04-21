from __future__ import annotations

from multi_agent_workbench.llm.client_base import LLMClientABC
from multi_agent_workbench.state.models import PlannerDecision, WorkbenchState


class PlannerAgent:
    name = "planner"

    def __init__(self, llm: LLMClientABC) -> None:
        self.llm = llm

    def run(self, state: WorkbenchState) -> PlannerDecision:
        system_prompt = (
            "You are a planning agent for a multi-agent document workbench. "
            "Decide whether the question can be answered directly, requires document retrieval, "
            "or requires tool usage. "
            "Return a JSON object with keys: "
            "mode, needs_retrieval, needs_tools, answer_strategy, rationale. "
            "Valid mode values are: answer_direct, retrieve, retrieve_and_tools."
        )

        user_prompt = (
            f"User query:\n{state.user_query}\n\n"
            "Choose the best plan for answering the query over a local document corpus."
        )

        data = self.llm.complete_json(system_prompt=system_prompt, user_prompt=user_prompt)

        decision = PlannerDecision(
            mode=str(data.get("mode", "retrieve")),
            needs_retrieval=bool(data.get("needs_retrieval", True)),
            needs_tools=bool(data.get("needs_tools", False)),
            answer_strategy=str(data.get("answer_strategy", "fallback_retrieval")),
            rationale=str(data.get("rationale", "No rationale provided.")),
        )

        state.planner_decision = decision
        return decision