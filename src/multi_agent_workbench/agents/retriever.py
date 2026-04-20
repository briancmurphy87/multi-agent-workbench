from __future__ import annotations

from multi_agent_workbench.retrieval.corpus import LoadedCorpus
from multi_agent_workbench.retrieval.search import lexical_search
from multi_agent_workbench.state.models import WorkbenchState


class RetrieverAgent:
    name = "retriever"

    def __init__(self, corpus: LoadedCorpus, top_k: int = 5) -> None:
        self.corpus = corpus
        self.top_k = top_k

    def run(self, state: WorkbenchState) -> None:
        state.retrieved_chunks = lexical_search(state.user_query, self.corpus, top_k=self.top_k)