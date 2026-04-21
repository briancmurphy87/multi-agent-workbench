from __future__ import annotations

from pydantic import BaseModel


class PlannerDecision(BaseModel):
    mode: str
    needs_retrieval: bool
    needs_tools: bool
    answer_strategy: str
    rationale: str