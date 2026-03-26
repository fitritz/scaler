from __future__ import annotations

from typing import Any, Dict, Optional

from src.env.graders import task_grading_summary
from src.env.models import Action, Observation, StepResult, Ticket
from src.env.rewards import compute_reward
from src.env.tasks import TASK_DEFINITIONS, build_tickets, list_tasks

UNSAFE_TERMS = ("disable all security", "share password", "bypass policy")


class SupportOpsEnv:
    def __init__(self) -> None:
        self.task_id: Optional[str] = None
        self.max_steps: int = 0
        self.step_count: int = 0
        self.tickets: list[Ticket] = []
        self.policy_violations: int = 0
        self.done: bool = False

    def reset(self, task_id: str = "easy_ticket_triage") -> Observation:
        if task_id not in TASK_DEFINITIONS:
            raise ValueError(f"Unknown task_id: {task_id}")

        self.task_id = task_id
        self.max_steps = int(TASK_DEFINITIONS[task_id]["max_steps"])
        self.step_count = 0
        self.policy_violations = 0
        self.done = False
        self.tickets = build_tickets(task_id)
        return self._observation()

    def step(self, action: Action) -> StepResult:
        if self.task_id is None:
            raise RuntimeError("Environment not initialized. Call reset() first.")
        if self.done:
            raise RuntimeError("Episode is done. Call reset() to start a new one.")

        self.step_count += 1
        ticket = self._get_ticket(action.ticket_id)
        changed = False
        policy_violation = False
        resolved_now = False
        info: Dict[str, Any] = {}

        if ticket is None and action.action_type not in {"request_info"}:
            info["warning"] = "ticket_id required for this action"

        if action.action_type == "classify_ticket" and ticket is not None and action.value:
            ticket.category = action.value
            changed = True
        elif action.action_type == "set_priority" and ticket is not None and action.value:
            ticket.priority = action.value
            changed = True
        elif action.action_type == "assign_team" and ticket is not None and action.value:
            ticket.team = action.value
            changed = True
        elif action.action_type == "request_info" and ticket is not None:
            ticket.clarification_requests += 1
            changed = True
        elif action.action_type == "draft_reply" and ticket is not None and action.value:
            reply = action.value.lower()
            changed = True
            if any(term in reply for term in UNSAFE_TERMS):
                ticket.policy_violation = True
                policy_violation = True
                self.policy_violations += 1
        elif action.action_type == "escalate" and ticket is not None:
            ticket.escalated = True
            changed = True
        elif action.action_type == "resolve" and ticket is not None:
            triage_ready = (
                ticket.category == ticket.expected_category
                and ticket.priority == ticket.expected_priority
                and ticket.team == ticket.expected_team
            )
            escalation_ready = (not ticket.requires_escalation) or ticket.escalated
            if triage_ready and escalation_ready and not ticket.policy_violation:
                ticket.resolved = True
                resolved_now = True
                changed = True
            else:
                info["warning"] = "resolve blocked: missing correct triage/escalation or policy violation"

        reward = compute_reward(ticket, action.action_type, changed, policy_violation, resolved_now)

        if self.step_count >= self.max_steps:
            self.done = True
        if self.tickets and all(t.resolved for t in self.tickets):
            self.done = True
        if self.policy_violations >= 3:
            self.done = True
            info["terminated_reason"] = "policy_violation_threshold"

        if self.done:
            info["grader"] = task_grading_summary(
                self.task_id,
                self.tickets,
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
            "tickets": [ticket.model_dump() for ticket in self.tickets],
        }

    def tasks(self) -> Dict[str, Any]:
        return {
            "tasks": list_tasks(),
            "action_schema": {
                "action_type": [
                    "classify_ticket",
                    "set_priority",
                    "assign_team",
                    "request_info",
                    "draft_reply",
                    "escalate",
                    "resolve",
                ],
                "ticket_id": "string (required for most actions)",
                "value": "string (used by classify/set/assign/draft)",
            },
        }

    def grader(self) -> Dict[str, float]:
        if self.task_id is None:
            raise RuntimeError("Environment not initialized. Call reset() first.")
        return task_grading_summary(
            self.task_id,
            self.tickets,
            self.policy_violations,
            self.step_count,
            self.max_steps,
        )

    def _observation(self) -> Observation:
        pending = [ticket.ticket_id for ticket in self.tickets if not ticket.resolved]
        return Observation(
            task_id=self.task_id or "uninitialized",
            step_count=self.step_count,
            max_steps=self.max_steps,
            queue_size=len(pending),
            pending_ticket_ids=pending,
            tickets=self.tickets,
        )

    def _get_ticket(self, ticket_id: Optional[str]) -> Optional[Ticket]:
        if ticket_id is None:
            return None
        for ticket in self.tickets:
            if ticket.ticket_id == ticket_id:
                return ticket
        return None
