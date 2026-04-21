from __future__ import annotations

import os

from multi_agent_workbench.llm.client_base import LLMClientABC
from multi_agent_workbench.llm.client_openai import LLMClientOpenAI
from multi_agent_workbench.llm.client_stub import LLMClientStub


def init_llm_client(model: str, api_key: str | None = None) -> LLMClientABC:
    api_key_final: str | None = api_key or os.getenv("OPENAI_API_KEY")
    if api_key_final is None or model == "stub-model":
        return LLMClientStub()
    else:
        from openai import OpenAI
        return LLMClientOpenAI(
            model=model,
            open_api_client=OpenAI(api_key=api_key_final),
        )
