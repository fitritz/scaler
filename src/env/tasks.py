from __future__ import annotations

from typing import Dict, List

from src.env.models import Incident


TASK_DEFINITIONS: Dict[str, Dict[str, object]] = {
    "easy_incident_triage": {
        "difficulty": "easy",
        "description": "Assess one incident with correct risk level, priority, and responder.",
        "max_steps": 10,
        "incidents": [
            {
                "incident_id": "I1",
                "report_text": "A woman reports repeated stalking near her home during late evening.",
                "expected_risk_level": "high",
                "expected_priority": "urgent",
                "expected_responder": "rapid_response_unit",
                "requires_authority_escalation": True,
            }
        ],
    },
    "dispatch_queue_management": {
        "difficulty": "medium",
        "description": "Manage multiple incident reports with proper prioritization and dispatch.",
        "max_steps": 24,
        "incidents": [
            {
                "incident_id": "I2",
                "report_text": "Harassment complaint at a crowded bus stop after dusk.",
                "expected_risk_level": "medium",
                "expected_priority": "high",
                "expected_responder": "local_patrol",
                "requires_authority_escalation": False,
            },
            {
                "incident_id": "I3",
                "report_text": "Caller reports suspicious vehicle following her for 20 minutes.",
                "expected_risk_level": "high",
                "expected_priority": "urgent",
                "expected_responder": "rapid_response_unit",
                "requires_authority_escalation": True,
            },
            {
                "incident_id": "I4",
                "report_text": "Request for safe accompaniment from metro station to hostel.",
                "expected_risk_level": "low",
                "expected_priority": "low",
                "expected_responder": "community_support",
                "requires_authority_escalation": False,
            },
        ],
    },
    "high_risk_safe_resolution": {
        "difficulty": "hard",
        "description": "Handle high-risk incidents with strict safety and escalation policy compliance.",
        "max_steps": 36,
        "incidents": [
            {
                "incident_id": "I5",
                "report_text": "Emergency distress call: threat reported near workplace parking at night.",
                "expected_risk_level": "critical",
                "expected_priority": "critical",
                "expected_responder": "emergency_response",
                "requires_authority_escalation": True,
            },
            {
                "incident_id": "I6",
                "report_text": "Digital blackmail complaint with immediate safety concern.",
                "expected_risk_level": "critical",
                "expected_priority": "critical",
                "expected_responder": "cyber_cell_coordination",
                "requires_authority_escalation": True,
            },
        ],
    },
}


def build_incidents(task_id: str) -> List[Incident]:
    task = TASK_DEFINITIONS[task_id]
    return [Incident(**item) for item in task["incidents"]]  # type: ignore[index]


def list_tasks() -> List[Dict[str, str]]:
    result: List[Dict[str, str]] = []
    for task_id, task in TASK_DEFINITIONS.items():
        result.append(
            {
                "task_id": task_id,
                "difficulty": str(task["difficulty"]),
                "description": str(task["description"]),
            }
        )
    return result
