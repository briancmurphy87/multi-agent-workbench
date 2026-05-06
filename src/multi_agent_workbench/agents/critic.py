from __future__ import annotations

import re

from multi_agent_workbench.state.models import WorkbenchState


_CITATION_RE = re.compile(r"\[[A-Za-z0-9_-]+-\d+\]")


class CriticAgent:
    name = "critic"

    def run(self, state: WorkbenchState) -> str:
        answer = state.draft_answer or ""
        query = state.user_query.lower()
        evidence_text = "\n\n".join(chunk.text for chunk in state.retrieved_chunks).lower()

        has_evidence = len(state.retrieved_chunks) > 0
        has_valid_citation = _has_valid_answer_citation(answer)
        is_stub_echo = _looks_like_stub_echo(answer)
        asks_for_specific_attribution = _asks_for_specific_attribution(query)

        if not has_evidence:
            verdict = "accept_with_insufficient_evidence"

        elif is_stub_echo and asks_for_specific_attribution:
            verdict = "accept_with_insufficient_evidence"

        elif asks_for_specific_attribution and not _evidence_supports_attribution_query(evidence_text):
            verdict = "accept_with_insufficient_evidence"

        elif not has_valid_citation:
            verdict = "retry_with_citations"

        else:
            verdict = "accept"

        state.critic_verdict = verdict
        return verdict


def _has_valid_answer_citation(answer: str) -> bool:
    if _looks_like_stub_echo(answer):
        answer_before_evidence = answer.split("Evidence:", maxsplit=1)[0]
        return bool(_CITATION_RE.search(answer_before_evidence))

    return bool(_CITATION_RE.search(answer))


def _looks_like_stub_echo(answer: str) -> bool:
    return "System prompt:" in answer and "User prompt:" in answer and "Evidence:" in answer


def _asks_for_specific_attribution(query: str) -> bool:
    attribution_markers = [
        "which engineer",
        "which developer",
        "which person",
        "who originally",
        "who approved",
        "who decided",
        "who found",
        "who fixed",
        "who authored",
        "who wrote",
    ]
    return any(marker in query for marker in attribution_markers)


def _evidence_supports_attribution_query(evidence_text: str) -> bool:
    attribution_evidence_markers = [
        "approved",
        "approval",
        "decided",
        "decision",
        "authored",
        "wrote",
        "found",
        "fixed",
        "developer",
        "engineer",
    ]
    return any(marker in evidence_text for marker in attribution_evidence_markers)