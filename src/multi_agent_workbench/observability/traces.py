from __future__ import annotations

import time
from contextlib import contextmanager

from src.multi_agent_workbench.state.models import AgentStep, WorkbenchState


@contextmanager
def traced_agent_step(state: WorkbenchState, agent_name: str, action: str, input_summary: str):
    started = time.time()
    output_summary = ""
    try:
        box: dict[str, str] = {"output_summary": ""}
        yield box
        output_summary = box.get("output_summary", "")
    finally:
        state.agent_steps.append(
            AgentStep(
                agent_name=agent_name,
                action=action,
                input_summary=input_summary,
                output_summary=output_summary,
                started_at=started,
                finished_at=time.time(),
            )
        )