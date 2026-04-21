from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time
import uuid

from multi_agent_workbench.agents.planner_models import PlannerDecision


@dataclass
class RetrievedChunk:
    doc_id: str
    chunk_id: str
    text: str
    score: float
    source_path: str


@dataclass
class ToolCall:
    tool_name: str
    arguments: dict[str, Any]
    result: dict[str, Any]
    started_at: float
    finished_at: float


@dataclass
class AgentStep:
    agent_name: str
    action: str
    input_summary: str
    output_summary: str
    started_at: float
    finished_at: float


@dataclass
class SupervisorDecision:
    action: str
    rationale: str
    retry_instruction: str | None = None


@dataclass
class WorkbenchState:
    user_query: str
    run_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.time)
    planner_decision: PlannerDecision | None = None
    retrieved_chunks: list[RetrievedChunk] = field(default_factory=list)
    tool_calls: list[ToolCall] = field(default_factory=list)
    agent_steps: list[AgentStep] = field(default_factory=list)
    draft_answer: str | None = None
    final_answer: str | None = None
    critic_verdict: str | None = None
    notes: list[str] = field(default_factory=list)
    artifacts: dict[str, Any] = field(default_factory=dict)
    supervisor_decision: SupervisorDecision | None = None