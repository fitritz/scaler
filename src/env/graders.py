from __future__ import annotations

from typing import Dict, List

from src.env.models import Ticket


def _ticket_triage_score(ticket: Ticket) -> float:
    checks = [
        ticket.category == ticket.expected_category,
        ticket.priority == ticket.expected_priority,
        ticket.team == ticket.expected_team,
    ]
    return sum(1 for ok in checks if ok) / 3.0


def grade_episode(task_id: str, tickets: List[Ticket], policy_violations: int, steps_used: int, max_steps: int) -> float:
    if not tickets:
        return 0.0

    triage_scores = [_ticket_triage_score(t) for t in tickets]
    avg_triage = sum(triage_scores) / len(triage_scores)

    resolved_ratio = sum(1 for t in tickets if t.resolved) / len(tickets)
    escalation_accuracy = sum(
        1
        for t in tickets
        if (t.requires_escalation and t.escalated) or (not t.requires_escalation and not t.escalated)
    ) / len(tickets)

    efficiency = max(0.0, 1.0 - (steps_used / max_steps))
    policy_score = max(0.0, 1.0 - 0.25 * policy_violations)

    if task_id == "easy_ticket_triage":
        score = 0.7 * avg_triage + 0.3 * resolved_ratio
    elif task_id == "queue_management":
        score = 0.5 * avg_triage + 0.3 * resolved_ratio + 0.2 * efficiency
    else:
        score = 0.35 * avg_triage + 0.3 * resolved_ratio + 0.2 * escalation_accuracy + 0.15 * policy_score

    return round(max(0.0, min(1.0, score)), 4)


def task_grading_summary(task_id: str, tickets: List[Ticket], policy_violations: int, steps_used: int, max_steps: int) -> Dict[str, float]:
    return {
        "score": grade_episode(task_id, tickets, policy_violations, steps_used, max_steps),
        "resolved_ratio": round(sum(1 for t in tickets if t.resolved) / max(1, len(tickets)), 4),
        "policy_violation_count": float(policy_violations),
    }
