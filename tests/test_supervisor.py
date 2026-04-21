from multi_agent_workbench.agents.supervisor import SupervisorAgent
from multi_agent_workbench.state.models import WorkbenchState


def test_supervisor_requests_retry_when_critic_wants_citations() -> None:
    state = WorkbenchState(user_query="test")
    state.critic_verdict = "retry_with_citations"
    state.draft_answer = "Some uncited answer."

    supervisor = SupervisorAgent()
    decision = supervisor.run(state)

    assert decision.action == "retry_responder"
    assert decision.retry_instruction is not None


def test_supervisor_finalizes_insufficient_evidence() -> None:
    state = WorkbenchState(user_query="test")
    state.critic_verdict = "accept_with_insufficient_evidence"
    state.draft_answer = "Not enough evidence."

    supervisor = SupervisorAgent()
    decision = supervisor.run(state)

    assert decision.action == "finalize_insufficient_evidence"


def test_supervisor_accepts_good_answer() -> None:
    state = WorkbenchState(user_query="test")
    state.critic_verdict = "accept"
    state.draft_answer = "Grounded answer [chunk-1]."

    supervisor = SupervisorAgent()
    decision = supervisor.run(state)

    assert decision.action == "accept"