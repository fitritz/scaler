from __future__ import annotations

from typing import Dict, List

from src.env.models import Incident


def _incident_alignment_score(incident: Incident) -> float:
    checks = [
        incident.risk_level == incident.expected_risk_level,
        incident.priority == incident.expected_priority,
        incident.responder == incident.expected_responder,
    ]
    return sum(1 for ok in checks if ok) / 3.0


def grade_episode(task_id: str, incidents: List[Incident], policy_violations: int, steps_used: int, max_steps: int) -> float:
    if not incidents:
        return 0.0

    alignment_scores = [_incident_alignment_score(i) for i in incidents]
    avg_alignment = sum(alignment_scores) / len(alignment_scores)

    closed_ratio = sum(1 for i in incidents if i.case_closed) / len(incidents)
    escalation_accuracy = sum(
        1
        for i in incidents
        if (i.requires_authority_escalation and i.escalated_to_authorities)
        or (not i.requires_authority_escalation and not i.escalated_to_authorities)
    ) / len(incidents)

    efficiency = max(0.0, 1.0 - (steps_used / max_steps))
    policy_score = max(0.0, 1.0 - 0.25 * policy_violations)

    if task_id == "easy_incident_triage":
        score = 0.7 * avg_alignment + 0.3 * closed_ratio
    elif task_id == "dispatch_queue_management":
        score = 0.5 * avg_alignment + 0.3 * closed_ratio + 0.2 * efficiency
    else:
        score = 0.35 * avg_alignment + 0.3 * closed_ratio + 0.2 * escalation_accuracy + 0.15 * policy_score

    return round(max(0.0, min(1.0, score)), 4)


def task_grading_summary(task_id: str, incidents: List[Incident], policy_violations: int, steps_used: int, max_steps: int) -> Dict[str, float]:
    return {
        "score": grade_episode(task_id, incidents, policy_violations, steps_used, max_steps),
        "closed_case_ratio": round(sum(1 for i in incidents if i.case_closed) / max(1, len(incidents)), 4),
        "policy_violation_count": float(policy_violations),
    }
