from __future__ import annotations

from pathlib import Path


def get_doc_metadata(path: str) -> dict[str, str | int]:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    return {
        "path": str(p),
        "filename": p.name,
        "doc_id": p.stem,
        "chars": len(text),
        "lines": text.count("\n") + 1,
    }