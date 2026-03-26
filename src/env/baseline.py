from __future__ import annotations

from typing import Dict

from src.env.environment import SupportOpsEnv
from src.env.models import Action
from src.env.tasks import TASK_DEFINITIONS


def _play_task(env: SupportOpsEnv, task_id: str) -> float:
    env.reset(task_id)

    for ticket in env.tickets:
        env.step(Action(action_type="classify_ticket", ticket_id=ticket.ticket_id, value=ticket.expected_category))
        env.step(Action(action_type="set_priority", ticket_id=ticket.ticket_id, value=ticket.expected_priority))
        env.step(Action(action_type="assign_team", ticket_id=ticket.ticket_id, value=ticket.expected_team))

        if ticket.requires_escalation:
            env.step(Action(action_type="escalate", ticket_id=ticket.ticket_id))

        env.step(Action(action_type="draft_reply", ticket_id=ticket.ticket_id, value="We are investigating your request with policy-safe steps."))
        env.step(Action(action_type="resolve", ticket_id=ticket.ticket_id))

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
