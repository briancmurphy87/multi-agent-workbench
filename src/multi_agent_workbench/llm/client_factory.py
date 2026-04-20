from __future__ import annotations

import os

from openai import OpenAI

from multi_agent_workbench.llm.client import LLMClient
from multi_agent_workbench.llm.client_state import ClientState
from multi_agent_workbench.llm.client_stub import LLMClientStub


def init_llm_client(model: str, api_key: str | None = None) -> LLMClient:
    api_key_final: str | None = api_key or os.getenv("OPENAI_API_KEY")
    if api_key_final is not None:
        return LLMClient(
            model=model,
            client_state=ClientState(
                open_api_client=OpenAI(api_key=api_key_final)
            ),
        )
    else:
        return LLMClientStub()
