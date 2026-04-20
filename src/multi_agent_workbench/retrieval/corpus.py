from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.multi_agent_workbench.retrieval.chunking import chunk_text


@dataclass
class CorpusChunk:
    doc_id: str
    chunk_id: str
    source_path: Path
    text: str


@dataclass
class LoadedCorpus:
    chunks: list[CorpusChunk]


def load_corpus(corpus_dir: Path) -> LoadedCorpus:
    chunks: list[CorpusChunk] = []
    for path in sorted(corpus_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for idx, chunk in enumerate(chunk_text(text)):
            chunks.append(
                CorpusChunk(
                    doc_id=path.stem,
                    chunk_id=f"{path.stem}-{idx}",
                    source_path=path,
                    text=chunk,
                )
            )
    return LoadedCorpus(chunks=chunks)