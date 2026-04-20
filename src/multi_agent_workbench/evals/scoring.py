from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EvalScore:
    keyword_hit_rate: float
    retrieval_used_correctly: bool
    produced_answer: bool


def score_case(
    final_answer: str | None,
    expected_keywords: list[str],
    requires_retrieval: bool,
    retrieved_count: int,
) -> EvalScore:
    answer = (final_answer or "").lower()
    hits = sum(1 for kw in expected_keywords if kw.lower() in answer)
    keyword_hit_rate = hits / len(expected_keywords) if expected_keywords else 1.0

    retrieval_used_correctly = (retrieved_count > 0) if requires_retrieval else True
    produced_answer = bool((final_answer or "").strip())

    return EvalScore(
        keyword_hit_rate=keyword_hit_rate,
        retrieval_used_correctly=retrieval_used_correctly,
        produced_answer=produced_answer,
    )