from __future__ import annotations

import argparse
from pathlib import Path

from src.multi_agent_workbench.agents.critic import CriticAgent
from src.multi_agent_workbench.agents.planner import PlannerAgent
from src.multi_agent_workbench.agents.responder import ResponderAgent
from src.multi_agent_workbench.agents.retriever import RetrieverAgent
from src.multi_agent_workbench.config import get_settings
from src.multi_agent_workbench.llm.client import LLMClient
from src.multi_agent_workbench.observability.artifacts import write_run_artifacts
from src.multi_agent_workbench.retrieval.corpus import load_corpus
from src.multi_agent_workbench.state.models import WorkbenchState
from src.multi_agent_workbench.workflows.simple_loop import SimpleWorkflow


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="multi-agent-workbench")
    sub = parser.add_subparsers(dest="command", required=True)

    ask = sub.add_parser("ask")
    ask.add_argument("--query", required=True)
    ask.add_argument("--corpus-dir", default=None)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    settings = get_settings()

    if args.command == "ask":
        corpus_dir = Path(args.corpus_dir) if args.corpus_dir else settings.corpus_dir
        corpus = load_corpus(corpus_dir)
        llm = LLMClient(model=settings.model)
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


if __name__ == "__main__":
    main()