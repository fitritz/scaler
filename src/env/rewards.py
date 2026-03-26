from __future__ import annotations

from typing import Dict, List

from src.env.models import Reward, Ticket


def compute_reward(
    ticket: Ticket | None,
    action_type: str,
    changed: bool,
    policy_violation: bool,
    resolved_now: bool,
) -> Reward:
    components: Dict[str, float] = {}
    violations: List[str] = []
    total = 0.0

    if not changed:
        components["no_progress"] = -0.1
        total -= 0.1

    if ticket is not None and changed:
        if action_type == "classify_ticket" and ticket.category == ticket.expected_category:
            components["correct_classification"] = 0.2
            total += 0.2
        elif action_type == "set_priority" and ticket.priority == ticket.expected_priority:
            components["correct_priority"] = 0.2
            total += 0.2
        elif action_type == "assign_team" and ticket.team == ticket.expected_team:
            components["correct_assignment"] = 0.2
            total += 0.2
        elif action_type == "request_info":
            components["clarification"] = 0.05
            total += 0.05
        elif action_type == "escalate" and ticket.requires_escalation and ticket.escalated:
            components["correct_escalation"] = 0.2
            total += 0.2
        elif action_type == "escalate" and not ticket.requires_escalation:
            components["wrong_escalation"] = -0.2
            total -= 0.2
        elif action_type == "draft_reply":
            components["response_attempt"] = 0.1
            total += 0.1

    if policy_violation:
        components["policy_violation"] = -0.3
        total -= 0.3
        violations.append("unsafe_response")

    if resolved_now:
        components["resolved"] = 0.2
        total += 0.2

    # Clamp to validator-friendly range.
    total = max(-1.0, min(1.0, total))
    return Reward(total=round(total, 4), components=components, policy_violations=violations)
