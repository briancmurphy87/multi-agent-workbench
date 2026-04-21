from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from multi_agent_workbench.evals.datasets import load_eval_cases
from multi_agent_workbench.evals.scoring import score_case
from multi_agent_workbench.llm.client_base import LLMClientABC
from multi_agent_workbench.llm.client_factory import init_llm_client
from multi_agent_workbench.observability.artifacts import write_run_artifacts
from multi_agent_workbench.retrieval.corpus import load_corpus
from multi_agent_workbench.state.models import WorkbenchState
from multi_agent_workbench.workflows.workflow_factory import init_workflow


def run_evals(
    cases_dir: Path,
    corpus_dir: Path,
    outputs_dir: Path,
    summaries_dir: Path,
    model: str,
    top_k: int,
) -> Path:
    cases = load_eval_cases(cases_dir)
    corpus = load_corpus(corpus_dir)
    llm: LLMClientABC = init_llm_client(model=model)

    outputs_dir.mkdir(parents=True, exist_ok=True)
    summaries_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict] = []

    for case in cases:
        workflow = init_workflow(
            corpus=corpus,
            top_k=top_k,
            llm=llm,
        )

        state = WorkbenchState(user_query=case.query)
        final_state = workflow.run(state)

        # agent = 'planner': extract fields before scoring
        planner_mode = (
            final_state.planner_decision.mode
            if final_state.planner_decision is not None
            else None
        )
        planner_needs_tools = (
            final_state.planner_decision.needs_tools
            if final_state.planner_decision is not None
            else None
        )
        planner_needs_retrieval = (
            final_state.planner_decision.needs_retrieval
            if final_state.planner_decision is not None
            else None
        )
        # agent = 'supervisor': extract fields before scoring
        supervisor_action = (
            final_state.supervisor_decision.action
            if final_state.supervisor_decision is not None
            else None
        )
        # agent = 'responder': count retries
        retry_count = sum(
            1
            for step in final_state.agent_steps
            if step.agent_name == "responder" and step.action == "respond_retry"
        )

        # write artifacts of just-executed 'run'
        dir_case_outputs_root = outputs_dir / case.case_id
        dir_case_outputs_root.mkdir(parents=True, exist_ok=True)
        write_run_artifacts(final_state, dir_case_outputs_root)

        score = score_case(
            final_answer=final_state.final_answer,
            expected_keywords=case.expected_keywords,
            requires_retrieval=case.requires_retrieval,
            retrieved_count=len(final_state.retrieved_chunks),
            planner_mode=planner_mode,
            planner_needs_tools=planner_needs_tools,
            planner_needs_retrieval=planner_needs_retrieval,
            expected_planner_mode=case.expected_planner_mode,
            expected_needs_tools=case.expected_needs_tools,
            supervisor_action=supervisor_action,
            retry_count=retry_count,
            expected_supervisor_action=case.expected_supervisor_action,
        )

        results.append(
            {
                "case_id": case.case_id,
                "query": case.query,
                "planner_decision": (
                    asdict(final_state.planner_decision)
                    if final_state.planner_decision is not None
                    else None
                ),
                "supervisor_decision": (
                    asdict(final_state.supervisor_decision)
                    if final_state.supervisor_decision is not None
                    else None
                ),
                "critic_verdict": final_state.critic_verdict,
                "retrieved_count": len(final_state.retrieved_chunks),
                "retry_count": retry_count,
                "final_answer": final_state.final_answer,
                "score": asdict(score),
            }
        )

    avg_keyword_hit_rate = sum(r["score"]["keyword_hit_rate"] for r in results) / len(results)
    retrieval_accuracy = sum(
        1 for r in results if r["score"]["retrieval_used_correctly"]
    ) / len(results)

    # aggregate metrics for agent = planner
    planner_mode_accuracy = sum(
        1 for r in results if r["score"]["planner_mode_correct"]
    ) / len(results)

    planner_tools_accuracy = sum(
        1 for r in results if r["score"]["planner_tools_correct"]
    ) / len(results)

    planner_retrieval_accuracy = sum(
        1 for r in results if r["score"]["planner_retrieval_correct"]
    ) / len(results)

    # aggregate metrics for agent = supervisor
    supervisor_action_accuracy = sum(
        1 for r in results if r["score"]["supervisor_action_correct"]
    ) / len(results)

    insufficient_evidence_accuracy = sum(
        1 for r in results if r["score"]["insufficient_evidence_handled_correctly"]
    ) / len(results)

    # agent = 'responder': agg retry metric
    retry_execution_accuracy = sum(
        1 for r in results if r["score"]["retry_executed_correctly"]
    ) / len(results)

    # package summary metrics
    summary = {
        "num_cases": len(results),
        "avg_keyword_hit_rate": avg_keyword_hit_rate,
        "retrieval_accuracy": retrieval_accuracy,
        "planner_mode_accuracy": planner_mode_accuracy,
        "planner_tools_accuracy": planner_tools_accuracy,
        "planner_retrieval_accuracy": planner_retrieval_accuracy,
        "supervisor_action_accuracy": supervisor_action_accuracy,
        "insufficient_evidence_accuracy": insufficient_evidence_accuracy,
        "retry_execution_accuracy": retry_execution_accuracy,
        "results": results,
    }
    # then write
    summary_path = summaries_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary_path