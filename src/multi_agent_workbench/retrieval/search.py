from __future__ import annotations

from collections import Counter
import math

from src.multi_agent_workbench.retrieval.corpus import LoadedCorpus

from src.multi_agent_workbench.state.models import RetrievedChunk


def _tokenize(text: str) -> list[str]:
    return [t.strip(".,:;!?()[]{}\"'").lower() for t in text.split() if t.strip()]


def lexical_search(query: str, corpus: LoadedCorpus, top_k: int = 5) -> list[RetrievedChunk]:
    query_terms = _tokenize(query)
    query_counts = Counter(query_terms)
    results: list[RetrievedChunk] = []

    for chunk in corpus.chunks:
        chunk_terms = _tokenize(chunk.text)
        chunk_counts = Counter(chunk_terms)
        score = 0.0
        for term, q_count in query_counts.items():
            score += q_count * chunk_counts.get(term, 0)
        score /= math.sqrt(max(len(chunk_terms), 1))
        if score > 0:
            results.append(
                RetrievedChunk(
                    doc_id=chunk.doc_id,
                    chunk_id=chunk.chunk_id,
                    text=chunk.text,
                    score=score,
                    source_path=str(chunk.source_path),
                )
            )

    results.sort(key=lambda x: x.score, reverse=True)
    return results[:top_k]