from __future__ import annotations
import pytest
from pathlib import Path

from multi_agent_workbench.agents.critic import CriticAgent
from multi_agent_workbench.agents.planner import PlannerAgent
from multi_agent_workbench.agents.responder import ResponderAgent
from multi_agent_workbench.agents.retriever import RetrieverAgent
from multi_agent_workbench.agents.supervisor import SupervisorAgent
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
        supervisor=SupervisorAgent(),
    )

    state = WorkbenchState(
        user_query=(
            "What changed in Northstar's ingestion pipeline between the current "
            "architecture and the latest release, and are there any operational "
            "caveats mentioned in the runbook?"
        )
    )

    # call: 'run'
    final_state = workflow.run(state)

    assert final_state.planner_decision.needs_retrieval
    assert len(final_state.retrieved_chunks) > 0
    assert final_state.final_answer is not None
    assert len(final_state.agent_steps) >= 4
    assert final_state.critic_verdict is not None
    # verify output: agent = 'supervisor'
    assert final_state.supervisor_decision is not None
    assert final_state.supervisor_decision.action in {
        "accept",
        "retry_responder",
        "finalize_insufficient_evidence",
    }


def test_langgraph_workflow_runs_end_to_end(tmp_path: Path) -> None:
    pytest.importorskip("langgraph")
    from multi_agent_workbench.workflows.langgraph_flow import LangGraphWorkflow
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
    workflow = LangGraphWorkflow(
        planner=PlannerAgent(llm=llm),
        retriever=RetrieverAgent(corpus=corpus, top_k=5),
        responder=ResponderAgent(llm=llm),
        critic=CriticAgent(),
        supervisor=SupervisorAgent(),
    )

    state = WorkbenchState(
        user_query=(
            "What changed in Northstar's ingestion pipeline between the current "
            "architecture and the latest release, and are there any operational "
            "caveats mentioned in the runbook?"
        )
    )

    # call: 'run'
    final_state = workflow.run(state)

    assert final_state.planner_decision.needs_retrieval
    assert len(final_state.retrieved_chunks) > 0
    assert final_state.final_answer is not None
    assert len(final_state.agent_steps) >= 4
    assert final_state.critic_verdict is not None
    # verify output: agent = 'supervisor'
    assert final_state.supervisor_decision is not None
    assert final_state.supervisor_decision.action in {
        "accept",
        "retry_responder",
        "finalize_insufficient_evidence",
    }

    """
    TODO: 
    separate dedicated retry-path test: force a case where supervisor chooses retry and then assert retry_count == 1
    will make your tests more stable.
    """
    # # there is a single retry
    # assert final_state.retry_count == 1

    # # TODO: decide if should be included?
    # # there is a respond_retry agent step
    # assert len(final_state.agent_steps) > 0
    # retry_step_indices = [
    #     step_i
    #     for step_i, step in enumerate(final_state.agent_steps)
    #     if step.agent_name == "responder" and step.action == "respond_retry"
    # ]
    # assert len(retry_step_indices) > 0

    # final answer exists
    assert final_state.final_answer is not None

"""
add dedicated retry-path test for both workflows

proves the one branch that matters most: 
supervisor-driven revision followed by re-supervision.

proves all of the important things:
- a retry actually happened
- exactly one retry happened
- the respond_retry step exists
- the final supervisor decision is no longer retry_responder
- the final answer contains citations
"""
def test_run_artifacts_are_written(tmp_path: Path) -> None:
    state = WorkbenchState(user_query="test query")
    state.final_answer = "hello world"

    run_dir = write_run_artifacts(state, tmp_path)

    assert run_dir.exists()
    assert (run_dir / "final_answer.md").exists()
    assert (run_dir / "trace.json").exists()
    assert (run_dir / "retrieved_chunks.json").exists()
    assert (run_dir / "artifacts.json").exists()


def test_simple_workflow_retry_path(tmp_path: Path) -> None:
    corpus = _build_retry_demo_corpus(tmp_path)
    llm = LLMClientStub()
    workflow = SimpleWorkflow(
        planner=PlannerAgent(llm=llm),
        retriever=RetrieverAgent(corpus=corpus, top_k=5),
        responder=ResponderAgent(llm=llm),
        critic=CriticAgent(),
        supervisor=SupervisorAgent(),
    )

    state = WorkbenchState(
        user_query=(
            "retry-demo: What changed in Northstar's ingestion pipeline, "
            "and what operational caveats are called out in the runbook?"
        )
    )

    final_state = workflow.run(state)
    _assert_retry_path(final_state)


def test_langgraph_workflow_retry_path(tmp_path: Path) -> None:
    pytest.importorskip("langgraph")
    from multi_agent_workbench.workflows.langgraph_flow import LangGraphWorkflow

    corpus = _build_retry_demo_corpus(tmp_path)
    llm = LLMClientStub()
    workflow = LangGraphWorkflow(
        planner=PlannerAgent(llm=llm),
        retriever=RetrieverAgent(corpus=corpus, top_k=5),
        responder=ResponderAgent(llm=llm),
        critic=CriticAgent(),
        supervisor=SupervisorAgent(),
    )

    state = WorkbenchState(
        user_query=(
            "retry-demo: What changed in Northstar's ingestion pipeline, "
            "and what operational caveats are called out in the runbook?"
        )
    )

    final_state = workflow.run(state)
    _assert_retry_path(final_state)


def _build_retry_demo_corpus(tmp_path: Path):
    corpus_dir = tmp_path / "docs_retry"
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
            "high-priority traffic to the batch fallback path. "
            "Memory pressure is a leading indicator of backpressure.\n"
        ),
    )

    return load_corpus(corpus_dir)


def _assert_retry_path(final_state: WorkbenchState) -> None:
    assert final_state.retry_count == 1

    retry_steps = [
        step
        for step in final_state.agent_steps
        if step.agent_name == "responder" and step.action == "respond_retry"
    ]
    assert len(retry_steps) == 1

    critique_retry_steps = [
        step
        for step in final_state.agent_steps
        if step.agent_name == "critic" and step.action == "critique_retry"
    ]
    assert len(critique_retry_steps) == 1

    supervisor_steps = [
        step
        for step in final_state.agent_steps
        if step.agent_name == "supervisor" and step.action == "supervise"
    ]
    assert len(supervisor_steps) >= 2

    assert final_state.supervisor_decision is not None
    assert final_state.supervisor_decision.action != "retry_responder"

    assert final_state.critic_verdict == "accept"
    assert final_state.final_answer is not None
    assert "[" in final_state.final_answer and "]" in final_state.final_answer
# if __name__ == "__main__":
#     import os
#     dir_curr: Path = Path(os.getcwd())
#     test_langgraph_workflow_runs_end_to_end(dir_curr)