from __future__ import annotations

from src.env.environment import SupportOpsEnv
from src.env.models import Action


def test_reset_step_state_cycle() -> None:
    env = SupportOpsEnv()
    obs = env.reset("easy_ticket_triage")

    assert obs.task_id == "easy_ticket_triage"
    assert obs.queue_size == 1

    ticket_id = obs.tickets[0].ticket_id
    result = env.step(Action(action_type="classify_ticket", ticket_id=ticket_id, value="account_access"))

    assert result.reward.total >= -1.0
    assert result.reward.total <= 1.0
    assert result.observation.step_count == 1

    state = env.state()
    assert state["initialized"] is True
    assert state["task_id"] == "easy_ticket_triage"
