from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


ActionType = Literal[
    "assess_risk",
    "set_priority",
    "assign_responder",
    "request_clarification",
    "send_safety_guidance",
    "escalate_authorities",
    "close_case",
]


class Incident(BaseModel):
    incident_id: str
    report_text: str
    expected_risk_level: str
    expected_priority: str
    expected_responder: str
    requires_authority_escalation: bool = False
    risk_level: Optional[str] = None
    priority: Optional[str] = None
    responder: Optional[str] = None
    escalated_to_authorities: bool = False
    case_closed: bool = False
    policy_violation: bool = False
    clarification_count: int = 0


class Observation(BaseModel):
    task_id: str
    step_count: int
    max_steps: int
    pending_incident_count: int
    pending_incident_ids: List[str]
    incidents: List[Incident]


class Action(BaseModel):
    action_type: ActionType
    incident_id: Optional[str] = None
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
