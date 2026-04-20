from __future__ import annotations

from src.multi_agent_workbench.state.models import WorkbenchState


class PlannerAgent:
    name = "planner"

    def run(self, state: WorkbenchState) -> str:
        query = state.user_query.lower()
        retrieval_triggers = ["what changed", "compare", "latest", "runbook", "release", "architecture"]
        decision = "retrieve" if any(t in query for t in retrieval_triggers) else "answer_direct"
        state.planner_decision = decision
        return decision