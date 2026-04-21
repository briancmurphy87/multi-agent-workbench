from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json


@dataclass
class EvalCase:
    case_id: str
    query: str
    expected_keywords: list[str]
    requires_retrieval: bool
    expected_planner_mode: str
    expected_needs_tools: bool
    expected_supervisor_action: str

def load_eval_cases(cases_dir: Path) -> list[EvalCase]:
    cases: list[EvalCase] = []
    for path in sorted(cases_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        cases.append(
            EvalCase(
                case_id=data["id"],
                query=data["query"],
                expected_keywords=data["expected_keywords"],
                requires_retrieval=data["requires_retrieval"],
                expected_planner_mode=data["expected_planner_mode"],
                expected_needs_tools=data["expected_needs_tools"],
                expected_supervisor_action=data["expected_supervisor_action"],
            )
        )
    return cases