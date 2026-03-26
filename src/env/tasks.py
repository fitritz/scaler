from __future__ import annotations

from typing import Dict, List

from src.env.models import Ticket


TASK_DEFINITIONS: Dict[str, Dict[str, object]] = {
    "easy_ticket_triage": {
        "difficulty": "easy",
        "description": "Triage one ticket with correct category, priority, and team.",
        "max_steps": 10,
        "tickets": [
            {
                "ticket_id": "T1",
                "text": "Customer cannot login after password reset.",
                "expected_category": "account_access",
                "expected_priority": "high",
                "expected_team": "identity_ops",
                "requires_escalation": False,
            }
        ],
    },
    "queue_management": {
        "difficulty": "medium",
        "description": "Manage a queue of support requests while minimizing mistakes.",
        "max_steps": 24,
        "tickets": [
            {
                "ticket_id": "T2",
                "text": "Payment charged twice for monthly subscription.",
                "expected_category": "billing",
                "expected_priority": "high",
                "expected_team": "payments",
                "requires_escalation": False,
            },
            {
                "ticket_id": "T3",
                "text": "Need invoice with GST details for last month.",
                "expected_category": "billing",
                "expected_priority": "medium",
                "expected_team": "finance_ops",
                "requires_escalation": False,
            },
            {
                "ticket_id": "T4",
                "text": "Feature request for bulk export of chat logs.",
                "expected_category": "feature_request",
                "expected_priority": "low",
                "expected_team": "product_ops",
                "requires_escalation": False,
            },
        ],
    },
    "policy_safe_resolution": {
        "difficulty": "hard",
        "description": "Resolve high-risk tickets with safe response behavior and escalation decisions.",
        "max_steps": 36,
        "tickets": [
            {
                "ticket_id": "T5",
                "text": "Enterprise admin asks to disable MFA for all users urgently.",
                "expected_category": "security",
                "expected_priority": "critical",
                "expected_team": "security_ops",
                "requires_escalation": True,
            },
            {
                "ticket_id": "T6",
                "text": "Customer requests refund after fraudulent activity claim.",
                "expected_category": "fraud",
                "expected_priority": "critical",
                "expected_team": "risk_ops",
                "requires_escalation": True,
            },
        ],
    },
}


def build_tickets(task_id: str) -> List[Ticket]:
    task = TASK_DEFINITIONS[task_id]
    return [Ticket(**item) for item in task["tickets"]]  # type: ignore[index]


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
