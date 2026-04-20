from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class Settings:
    model: str = os.getenv("OPENAI_MODEL", "gpt-5")
    corpus_dir: Path = Path(os.getenv("MAW_CORPUS_DIR", "data/corpus/docs"))
    runs_dir: Path = Path(os.getenv("MAW_RUNS_DIR", "runs"))
    top_k: int = int(os.getenv("MAW_TOP_K", "5"))


def get_settings() -> Settings:
    return Settings()