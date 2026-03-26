from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


ActionType = Literal[
    "classify_ticket",
    "set_priority",
    "assign_team",
    "request_info",
    "draft_reply",
    "escalate",
    "resolve",
]


class Ticket(BaseModel):
    ticket_id: str
    text: str
    expected_category: str
    expected_priority: str
    expected_team: str
    requires_escalation: bool = False
    category: Optional[str] = None
    priority: Optional[str] = None
    team: Optional[str] = None
    escalated: bool = False
    resolved: bool = False
    policy_violation: bool = False
    clarification_requests: int = 0


class Observation(BaseModel):
    task_id: str
    step_count: int
    max_steps: int
    queue_size: int
    pending_ticket_ids: List[str]
    tickets: List[Ticket]


class Action(BaseModel):
    action_type: ActionType
    ticket_id: Optional[str] = None
    value: Optional[str] = None


class Reward(BaseModel):
    total: float = Field(ge=-1.0, le=1.0)
    components: Dict[str, float] = Field(default_factory=dict)
    policy_violations: List[str] = Field(default_factory=list)


class StepResult(BaseModel):
    observation: Observation
    reward: Reward
    done: bool
    info: Dict[str, Any] = Field(default_factory=dict)
