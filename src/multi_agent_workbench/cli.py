from __future__ import annotations

import argparse
from pathlib import Path

from multi_agent_workbench.agents.critic import CriticAgent
from multi_agent_workbench.agents.planner import PlannerAgent
from multi_agent_workbench.agents.responder import ResponderAgent
from multi_agent_workbench.agents.retriever import RetrieverAgent
from multi_agent_workbench.config import get_settings
from multi_agent_workbench.evals.runner import run_evals
from multi_agent_workbench.llm.client_factory import init_llm_client
from multi_agent_workbench.observability.artifacts import write_run_artifacts
from multi_agent_workbench.retrieval.corpus import load_corpus
from multi_agent_workbench.state.models import WorkbenchState
from multi_agent_workbench.workflows.simple_loop import SimpleWorkflow


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="multi-agent-workbench")
    sub = parser.add_subparsers(dest="command", required=True)

    ask = sub.add_parser("ask")
    ask.add_argument("--query", required=True)
    ask.add_argument("--corpus-dir", default=None)

    eval_cmd = sub.add_parser("eval")
    eval_cmd.add_argument("--cases-dir", default="evals/cases")
    eval_cmd.add_argument("--corpus-dir", default=None)
    eval_cmd.add_argument("--outputs-dir", default="evals/outputs")
    eval_cmd.add_argument("--summaries-dir", default="evals/summaries")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    settings = get_settings()

    if args.command == "ask":
        corpus_dir = Path(args.corpus_dir) if args.corpus_dir else settings.corpus_dir
        corpus = load_corpus(corpus_dir)
        llm = init_llm_client(model=settings.model)
        workflow = SimpleWorkflow(
            planner=PlannerAgent(),
            retriever=RetrieverAgent(corpus=corpus, top_k=settings.top_k),
            responder=ResponderAgent(llm=llm),
            critic=CriticAgent(),
        )
        state = WorkbenchState(user_query=args.query)
        final_state = workflow.run(state)
        run_dir = write_run_artifacts(final_state, settings.runs_dir)
        print(final_state.final_answer or "")
        print(f"\nArtifacts written to: {run_dir}")

    elif args.command == "eval":
        corpus_dir = Path(args.corpus_dir) if args.corpus_dir else settings.corpus_dir
        summary_path = run_evals(
            cases_dir=Path(args.cases_dir),
            corpus_dir=corpus_dir,
            outputs_dir=Path(args.outputs_dir),
            summaries_dir=Path(args.summaries_dir),
            model=settings.model,
            top_k=settings.top_k,
        )
        print(f"Eval summary written to: {summary_path}")

    else:
        raise ValueError(f"Unknown command: {args.command}")

if __name__ == "__main__":
    main()