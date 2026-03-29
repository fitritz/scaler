from __future__ import annotations

from src.env.environment import SupportOpsEnv
from src.env.models import Action


def test_reset_step_state_cycle() -> None:
    env = SupportOpsEnv()
    obs = env.reset("easy_incident_triage")

    assert obs.task_id == "easy_incident_triage"
    assert obs.pending_incident_count == 1

    incident_id = obs.incidents[0].incident_id
    result = env.step(Action(action_type="assess_risk", incident_id=incident_id, value="high"))

    assert result.reward.total >= -1.0
    assert result.reward.total <= 1.0
    assert result.observation.step_count == 1

    state = env.state()
    assert state["initialized"] is True
    assert state["task_id"] == "easy_incident_triage"
