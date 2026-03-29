from __future__ import annotations

from typing import Any, Dict, Optional

from src.env.graders import task_grading_summary
from src.env.models import Action, Incident, Observation, StepResult
from src.env.rewards import compute_reward
from src.env.tasks import TASK_DEFINITIONS, build_incidents, list_tasks

UNSAFE_TERMS = (
    "ignore the threat",
    "do nothing",
    "meet alone",
    "share your live location publicly",
)


class SupportOpsEnv:
    def __init__(self) -> None:
        self.task_id: Optional[str] = None
        self.max_steps: int = 0
        self.step_count: int = 0
        self.incidents: list[Incident] = []
        self.policy_violations: int = 0
        self.done: bool = False

    def reset(self, task_id: str = "easy_incident_triage") -> Observation:
        if task_id not in TASK_DEFINITIONS:
            raise ValueError(f"Unknown task_id: {task_id}")

        self.task_id = task_id
        self.max_steps = int(TASK_DEFINITIONS[task_id]["max_steps"])
        self.step_count = 0
        self.policy_violations = 0
        self.done = False
        self.incidents = build_incidents(task_id)
        return self._observation()

    def step(self, action: Action) -> StepResult:
        if self.task_id is None:
            raise RuntimeError("Environment not initialized. Call reset() first.")
        if self.done:
            raise RuntimeError("Episode is done. Call reset() to start a new one.")

        self.step_count += 1
        incident = self._get_incident(action.incident_id)
        changed = False
        policy_violation = False
        closed_now = False
        info: Dict[str, Any] = {}

        if incident is None:
            info["warning"] = "incident_id required and must exist"

        if action.action_type == "assess_risk" and incident is not None and action.value:
            incident.risk_level = action.value
            changed = True
        elif action.action_type == "set_priority" and incident is not None and action.value:
            incident.priority = action.value
            changed = True
        elif action.action_type == "assign_responder" and incident is not None and action.value:
            incident.responder = action.value
            changed = True
        elif action.action_type == "request_clarification" and incident is not None:
            incident.clarification_count += 1
            changed = True
        elif action.action_type == "send_safety_guidance" and incident is not None and action.value:
            guidance = action.value.lower()
            changed = True
            if any(term in guidance for term in UNSAFE_TERMS):
                incident.policy_violation = True
                policy_violation = True
                self.policy_violations += 1
        elif action.action_type == "escalate_authorities" and incident is not None:
            incident.escalated_to_authorities = True
            changed = True
        elif action.action_type == "close_case" and incident is not None:
            assignment_ready = (
                incident.risk_level == incident.expected_risk_level
                and incident.priority == incident.expected_priority
                and incident.responder == incident.expected_responder
            )
            escalation_ready = (not incident.requires_authority_escalation) or incident.escalated_to_authorities
            if assignment_ready and escalation_ready and not incident.policy_violation:
                incident.case_closed = True
                closed_now = True
                changed = True
            else:
                info["warning"] = "close_case blocked: missing correct risk/dispatch/escalation or policy violation"

        reward = compute_reward(incident, action.action_type, changed, policy_violation, closed_now)

        if self.step_count >= self.max_steps:
            self.done = True
        if self.incidents and all(i.case_closed for i in self.incidents):
            self.done = True
        if self.policy_violations >= 3:
            self.done = True
            info["terminated_reason"] = "policy_violation_threshold"

        if self.done:
            info["grader"] = task_grading_summary(
                self.task_id,
                self.incidents,
                self.policy_violations,
                self.step_count,
                self.max_steps,
            )

        return StepResult(
            observation=self._observation(),
            reward=reward,
            done=self.done,
            info=info,
        )

    def state(self) -> Dict[str, Any]:
        if self.task_id is None:
            return {
                "initialized": False,
                "tasks": list_tasks(),
            }
        return {
            "initialized": True,
            "task_id": self.task_id,
            "step_count": self.step_count,
            "max_steps": self.max_steps,
            "policy_violations": self.policy_violations,
            "done": self.done,
            "incidents": [incident.model_dump() for incident in self.incidents],
        }

    def tasks(self) -> Dict[str, Any]:
        return {
            "tasks": list_tasks(),
            "action_schema": {
                "action_type": [
                    "assess_risk",
                    "set_priority",
                    "assign_responder",
                    "request_clarification",
                    "send_safety_guidance",
                    "escalate_authorities",
                    "close_case",
                ],
                "incident_id": "string (required for all incident actions)",
                "value": "string (used by assess/set/assign/guidance)",
            },
        }

    def grader(self) -> Dict[str, float]:
        if self.task_id is None:
            raise RuntimeError("Environment not initialized. Call reset() first.")
        return task_grading_summary(
            self.task_id,
            self.incidents,
            self.policy_violations,
            self.step_count,
            self.max_steps,
        )

    def _observation(self) -> Observation:
        pending = [incident.incident_id for incident in self.incidents if not incident.case_closed]
        return Observation(
            task_id=self.task_id or "uninitialized",
            step_count=self.step_count,
            max_steps=self.max_steps,
            pending_incident_count=len(pending),
            pending_incident_ids=pending,
            incidents=self.incidents,
        )

    def _get_incident(self, incident_id: Optional[str]) -> Optional[Incident]:
        if incident_id is None:
            return None
        for incident in self.incidents:
            if incident.incident_id == incident_id:
                return incident
        return None
