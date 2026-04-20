from __future__ import annotations

from typing import Any
import os
import time

from multi_agent_workbench.llm.result import LLMResult
from openai import OpenAI

class ClientState:
    def __init__(
            self, open_api_client: OpenAI | None
    ) -> None:
        # self.api_key = api_key
        self.open_api_client = open_api_client
