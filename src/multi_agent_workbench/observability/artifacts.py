from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import json

from multi_agent_workbench.state.models import WorkbenchState


def write_run_artifacts(state: WorkbenchState, runs_dir: Path) -> Path:
    run_dir = runs_dir / state.run_id
    return write_run_artifacts_to_dir(state=state, run_dir=run_dir)
    # run_dir.mkdir(parents=True, exist_ok=True)
    #
    # (run_dir / "final_answer.md").write_text(state.final_answer or state.draft_answer or "", encoding="utf-8")
    # (run_dir / "trace.json").write_text(
    #     json.dumps([asdict(step) for step in state.agent_steps], indent=2),
    #     encoding="utf-8",
    # )
    # (run_dir / "retrieved_chunks.json").write_text(
    #     json.dumps([asdict(chunk) for chunk in state.retrieved_chunks], indent=2),
    #     encoding="utf-8",
    # )
    # (run_dir / "artifacts.json").write_text(
    #     json.dumps(state.artifacts, indent=2),
    #     encoding="utf-8",
    # )
    # return run_dir


def write_run_artifacts_to_dir(state: WorkbenchState, run_dir: Path) -> Path:
    run_dir.mkdir(parents=True, exist_ok=True)

    (run_dir / "final_answer.md").write_text(state.final_answer or state.draft_answer or "", encoding="utf-8")
    (run_dir / "trace.json").write_text(
        json.dumps([asdict(step) for step in state.agent_steps], indent=2),
        encoding="utf-8",
    )
    (run_dir / "retrieved_chunks.json").write_text(
        json.dumps([chunk.model_dump_json() for chunk in state.retrieved_chunks], indent=2),
        encoding="utf-8",
    )
    (run_dir / "artifacts.json").write_text(
        json.dumps(state.artifacts, indent=2),
        encoding="utf-8",
    )
    return run_dir