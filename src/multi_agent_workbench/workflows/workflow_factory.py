from typing import Literal

from multi_agent_workbench.agents.critic import CriticAgent
from multi_agent_workbench.agents.planner import PlannerAgent
from multi_agent_workbench.agents.responder import ResponderAgent
from multi_agent_workbench.agents.retriever import RetrieverAgent
from multi_agent_workbench.agents.supervisor import SupervisorAgent
from multi_agent_workbench.llm.client_base import LLMClientABC
from multi_agent_workbench.retrieval.corpus import LoadedCorpus
from multi_agent_workbench.workflows.langgraph_flow import LangGraphWorkflow
from multi_agent_workbench.workflows.simple_loop import SimpleWorkflow

WorkflowTypesLiteral = Literal["simple", "langgraph"]
WorkflowType = SimpleWorkflow | LangGraphWorkflow

def init_workflow(
    corpus: LoadedCorpus,
    top_k: int,
    llm: LLMClientABC,
    workflow_type: WorkflowTypesLiteral = "simple",
) -> WorkflowType:
    # TODO: change default to 'LangGraph'
    if workflow_type == "langgraph":
        return LangGraphWorkflow(
            planner=PlannerAgent(llm=llm),
            retriever=RetrieverAgent(corpus=corpus, top_k=top_k),
            responder=ResponderAgent(llm=llm),
            critic=CriticAgent(),
            supervisor=SupervisorAgent(),
        )
    elif workflow_type == "simple":
        return SimpleWorkflow(
            planner=PlannerAgent(llm=llm),
            retriever=RetrieverAgent(corpus=corpus, top_k=top_k),
            responder=ResponderAgent(llm=llm),
            critic=CriticAgent(),
            supervisor=SupervisorAgent(),
        )
    else:
        raise ValueError(f"Unknown workflow type: {workflow_type}")