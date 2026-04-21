from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EvalScore:
    keyword_hit_rate: float
    retrieval_used_correctly: bool
    produced_answer: bool
    planner_mode_correct: bool
    planner_tools_correct: bool
    planner_retrieval_correct: bool
    supervisor_action_correct: bool
    insufficient_evidence_handled_correctly: bool


def score_case(
    final_answer: str | None,
    expected_keywords: list[str],
    requires_retrieval: bool,
    retrieved_count: int,
    planner_mode: str | None,
    planner_needs_tools: bool | None,
    planner_needs_retrieval: bool | None,
    expected_planner_mode: str,
    expected_needs_tools: bool,
    supervisor_action: str | None,
    expected_supervisor_action: str,
) -> EvalScore:
    answer = (final_answer or "").lower()
    hits = sum(1 for kw in expected_keywords if kw.lower() in answer)
    keyword_hit_rate = hits / len(expected_keywords) if expected_keywords else 1.0

    retrieval_used_correctly = (retrieved_count > 0) if requires_retrieval else (retrieved_count == 0)
    produced_answer = bool((final_answer or "").strip())

    planner_mode_correct = planner_mode == expected_planner_mode
    planner_tools_correct = planner_needs_tools == expected_needs_tools
    planner_retrieval_correct = planner_needs_retrieval == requires_retrieval

    supervisor_action_correct = supervisor_action == expected_supervisor_action

    insufficient_evidence_handled_correctly = True
    if expected_supervisor_action == "finalize_insufficient_evidence":
        insufficient_evidence_handled_correctly = (
            supervisor_action == "finalize_insufficient_evidence"
            and any(
                phrase in answer
                for phrase in [
                    "not enough evidence",
                    "insufficient",
                    "not provided",
                    "cannot answer confidently",
                ]
            )
        )

    return EvalScore(
        keyword_hit_rate=keyword_hit_rate,
        retrieval_used_correctly=retrieval_used_correctly,
        produced_answer=produced_answer,
        planner_mode_correct=planner_mode_correct,
        planner_tools_correct=planner_tools_correct,
        planner_retrieval_correct=planner_retrieval_correct,
        supervisor_action_correct=supervisor_action_correct,
        insufficient_evidence_handled_correctly=insufficient_evidence_handled_correctly,
    )