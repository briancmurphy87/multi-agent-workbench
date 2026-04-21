from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PlannerDecision:
    mode: str
    needs_retrieval: bool
    needs_tools: bool
    answer_strategy: str
    rationale: str