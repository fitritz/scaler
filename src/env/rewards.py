from __future__ import annotations

from typing import Dict, List

from src.env.models import Incident, Reward


def compute_reward(
    incident: Incident | None,
    action_type: str,
    changed: bool,
    policy_violation: bool,
    closed_now: bool,
) -> Reward:
    components: Dict[str, float] = {}
    violations: List[str] = []
    total = 0.0

    if not changed:
        components["no_progress"] = -0.1
        total -= 0.1

    if incident is not None and changed:
        if action_type == "assess_risk" and incident.risk_level == incident.expected_risk_level:
            components["correct_risk_assessment"] = 0.25
            total += 0.25
        elif action_type == "set_priority" and incident.priority == incident.expected_priority:
            components["correct_priority"] = 0.2
            total += 0.2
        elif action_type == "assign_responder" and incident.responder == incident.expected_responder:
            components["correct_dispatch"] = 0.2
            total += 0.2
        elif action_type == "request_clarification":
            components["clarification"] = 0.05
            total += 0.05
        elif action_type == "escalate_authorities" and incident.requires_authority_escalation and incident.escalated_to_authorities:
            components["correct_escalation"] = 0.2
            total += 0.2
        elif action_type == "escalate_authorities" and not incident.requires_authority_escalation:
            components["wrong_escalation"] = -0.2
            total -= 0.2
        elif action_type == "send_safety_guidance":
            components["safety_guidance"] = 0.1
            total += 0.1

    if policy_violation:
        components["policy_violation"] = -0.3
        total -= 0.3
        violations.append("unsafe_response")

    if closed_now:
        components["case_closed"] = 0.2
        total += 0.2

    # Clamp to validator-friendly range.
    total = max(-1.0, min(1.0, total))
    return Reward(total=round(total, 4), components=components, policy_violations=violations)
