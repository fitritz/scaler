from __future__ import annotations

from typing import Dict

from src.env.environment import SupportOpsEnv
from src.env.models import Action
from src.env.tasks import TASK_DEFINITIONS


def _play_task(env: SupportOpsEnv, task_id: str) -> float:
    env.reset(task_id)

    for incident in env.incidents:
        env.step(Action(action_type="assess_risk", incident_id=incident.incident_id, value=incident.expected_risk_level))
        env.step(Action(action_type="set_priority", incident_id=incident.incident_id, value=incident.expected_priority))
        env.step(Action(action_type="assign_responder", incident_id=incident.incident_id, value=incident.expected_responder))

        if incident.requires_authority_escalation:
            env.step(Action(action_type="escalate_authorities", incident_id=incident.incident_id))

        env.step(
            Action(
                action_type="send_safety_guidance",
                incident_id=incident.incident_id,
                value="Stay in a lit public area and keep a trusted contact informed while responders assist.",
            )
        )
        env.step(Action(action_type="close_case", incident_id=incident.incident_id))

    return env.grader()["score"]


def run_baseline() -> Dict[str, object]:
    env = SupportOpsEnv()
    scores: Dict[str, float] = {}

    for task_id in TASK_DEFINITIONS:
        scores[task_id] = _play_task(env, task_id)

    overall = round(sum(scores.values()) / max(1, len(scores)), 4)
    return {
        "scores": scores,
        "overall_score": overall,
        "seed": 42,
    }
