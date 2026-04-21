# ----------------------------
# LLM interface
# ----------------------------
from __future__ import annotations
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from multi_agent_workbench.llm.client_state import ClientState
from multi_agent_workbench.llm.result import LLMResult


class LLMClientABC(ABC):
    def __init__(
            self,
            model: str,
            client_state: ClientState,
    ) -> None:
        self.model = model
        self._client_state = client_state

    @abstractmethod
    def complete_text(self, system_prompt: str, user_prompt: str) -> LLMResult:
        raise NotImplementedError("Implement in derived class; method: 'complete_text'")

    def complete_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        raise NotImplementedError("Implement in derived class; method: 'complete_json'")
