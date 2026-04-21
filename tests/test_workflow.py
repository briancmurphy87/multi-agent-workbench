from __future__ import annotations

from pathlib import Path

from multi_agent_workbench.agents.critic import CriticAgent
from multi_agent_workbench.agents.planner import PlannerAgent
from multi_agent_workbench.agents.responder import ResponderAgent
from multi_agent_workbench.agents.retriever import RetrieverAgent
from multi_agent_workbench.observability.artifacts import write_run_artifacts
from multi_agent_workbench.retrieval.corpus import load_corpus
from multi_agent_workbench.state.models import WorkbenchState
from multi_agent_workbench.workflows.simple_loop import SimpleWorkflow

from multi_agent_workbench.llm.client_stub import LLMClientStub

"""
This gives you a real first test that:
- builds a temp corpus
- runs the workflow
- verifies retrieval happened
- verifies artifacts were written
"""

def _write_doc(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def test_simple_workflow_runs_end_to_end(tmp_path: Path) -> None:
    corpus_dir = tmp_path / "docs"
    corpus_dir.mkdir(parents=True)

    _write_doc(
        corpus_dir / "architecture.md",
        (
            "# Architecture\n\n"
            "Northstar historically used a batch-first ingestion design. "
            "Events were normalized every 15 minutes.\n"
        ),
    )
    _write_doc(
        corpus_dir / "release_notes.md",
        (
            "# Release Notes\n\n"
            "Version 2.4 introduced a streaming ingestion path and reduced "
            "priority traffic latency to under 90 seconds.\n"
        ),
    )
    _write_doc(
        corpus_dir / "runbook.md",
        (
            "# Runbook\n\n"
            "If stream processor lag exceeds 5 minutes, operators should divert "
            "high-priority traffic to the batch fallback path.\n"
        ),
    )

    corpus = load_corpus(corpus_dir)
    llm = LLMClientStub()
    workflow = SimpleWorkflow(
        planner=PlannerAgent(llm=llm),
        retriever=RetrieverAgent(corpus=corpus, top_k=5),
        responder=ResponderAgent(llm=llm),
        critic=CriticAgent(),
    )

    state = WorkbenchState(
        user_query=(
            "What changed in Northstar's ingestion pipeline between the current "
            "architecture and the latest release, and are there any operational "
            "caveats mentioned in the runbook?"
        )
    )

    final_state = workflow.run(state)

    assert final_state.planner_decision.needs_retrieval
    assert len(final_state.retrieved_chunks) > 0
    assert final_state.final_answer is not None
    assert len(final_state.agent_steps) >= 4
    assert final_state.critic_verdict is not None


def test_run_artifacts_are_written(tmp_path: Path) -> None:
    state = WorkbenchState(user_query="test query")
    state.final_answer = "hello world"

    run_dir = write_run_artifacts(state, tmp_path)

    assert run_dir.exists()
    assert (run_dir / "final_answer.md").exists()
    assert (run_dir / "trace.json").exists()
    assert (run_dir / "retrieved_chunks.json").exists()
    assert (run_dir / "artifacts.json").exists()


# if __name__ == "__main__":
#     dir_curr: Path = Path(os.getcwd())