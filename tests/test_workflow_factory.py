import pytest
from pathlib import Path

from multi_agent_workbench.llm.client_stub import LLMClientStub
from multi_agent_workbench.retrieval.corpus import CorpusChunk, LoadedCorpus
from multi_agent_workbench.workflows.langgraph_flow import LangGraphWorkflow
from multi_agent_workbench.workflows.simple_loop import SimpleWorkflow
from multi_agent_workbench.workflows.workflow_factory import init_workflow, WorkflowTypesLiteral, WorkflowType


def _test_case_common(
        workflow_type: type[WorkflowType],
        workflow_type_literal: WorkflowTypesLiteral
) -> None:
    chunks = 5
    corpus = LoadedCorpus(
        chunks=[
            CorpusChunk(
                doc_id=f"ID:{i}",
                chunk_id=f"{i}",
                source_path=Path(".") / f"chunk-{i}.txt",
                text=f"TEXT:{i}",
            )
            for i in range(0, chunks)
        ],
    )
    realized_workflow = init_workflow(corpus=corpus, top_k=5, llm=LLMClientStub(), workflow_type=workflow_type_literal)
    assert isinstance(realized_workflow, workflow_type), f"|expected={workflow_type} |realized={type(realized_workflow)}"

def test_init_workflow_simple() -> None:
    _test_case_common(SimpleWorkflow, "simple")



def test_init_workflow_langgraph() -> None:
    pytest.importorskip("langgraph")
    _test_case_common(LangGraphWorkflow, "langgraph")
