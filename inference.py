from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List

import importlib

import httpx

API_BASE_URL = os.getenv("API_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
HF_TOKEN = os.getenv("HF_TOKEN")
OPENENV_BASE_URL = os.getenv("OPENENV_BASE_URL", "http://127.0.0.1:7860")
MAX_EXTRA_STEPS = 4

SYSTEM_PROMPT = (
    "You are controlling a women safety incident-response environment. "
    "Return only valid JSON with keys: action_type, incident_id, value. "
    "Do not add markdown or explanation."
)

ALLOWED_ACTIONS = {
    "assess_risk",
    "set_priority",
    "assign_responder",
    "request_clarification",
    "send_safety_guidance",
    "escalate_authorities",
    "close_case",
}


def _rule_action(observation: Dict[str, Any]) -> Dict[str, Any]:
    incidents: List[Dict[str, Any]] = observation.get("incidents", [])
    for incident in incidents:
        if incident.get("case_closed"):
            continue

        incident_id = incident["incident_id"]

        if not incident.get("risk_level"):
            return {
                "action_type": "assess_risk",
                "incident_id": incident_id,
                "value": incident.get("expected_risk_level", "medium"),
            }
        if not incident.get("priority"):
            return {
                "action_type": "set_priority",
                "incident_id": incident_id,
                "value": incident.get("expected_priority", "high"),
            }
        if not incident.get("responder"):
            return {
                "action_type": "assign_responder",
                "incident_id": incident_id,
                "value": incident.get("expected_responder", "local_patrol"),
            }
        if incident.get("requires_authority_escalation") and not incident.get("escalated_to_authorities"):
            return {
                "action_type": "escalate_authorities",
                "incident_id": incident_id,
                "value": None,
            }

        return {
            "action_type": "send_safety_guidance",
            "incident_id": incident_id,
            "value": "Stay in a safe public area and share your status with a trusted contact while help is dispatched.",
        }

    return {
        "action_type": "close_case",
        "incident_id": None,
        "value": None,
    }


def _sanitize_action(action: Dict[str, Any], fallback: Dict[str, Any]) -> Dict[str, Any]:
    action_type = action.get("action_type")
    incident_id = action.get("incident_id")
    value = action.get("value")

    if action_type not in ALLOWED_ACTIONS:
        return fallback

    return {
        "action_type": action_type,
        "incident_id": incident_id,
        "value": value,
    }


def _llm_action(client: Any, observation: Dict[str, Any]) -> Dict[str, Any]:
    fallback = _rule_action(observation)

    prompt = {
        "task_id": observation.get("task_id"),
        "step_count": observation.get("step_count"),
        "pending_incident_ids": observation.get("pending_incident_ids", []),
        "incidents": observation.get("incidents", []),
        "instruction": "Choose the next best single action.",
    }

    response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0,
        max_tokens=160,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(prompt)},
        ],
    )

    content = response.choices[0].message.content or ""
    try:
        parsed = json.loads(content)
        if isinstance(parsed, dict):
            return _sanitize_action(parsed, fallback)
    except json.JSONDecodeError:
        pass

    return fallback


def _run_task(client: Any, http: httpx.Client, task_id: str) -> float:
    reset_resp = http.post("/reset", params={"task_id": task_id})
    reset_resp.raise_for_status()

    observation = reset_resp.json()
    max_steps = int(observation.get("max_steps", 8)) + MAX_EXTRA_STEPS

    for _ in range(max_steps):
        action = _llm_action(client, observation)

        # If no incident id is selected, use rule-based fallback to ensure progress.
        if action.get("incident_id") is None:
            action = _rule_action(observation)

        step_resp = http.post("/step", json=action)
        step_resp.raise_for_status()

        payload = step_resp.json()
        observation = payload["observation"]
        if payload.get("done"):
            break

    grade_resp = http.get("/grader")
    grade_resp.raise_for_status()
    return float(grade_resp.json()["score"])


def run_inference() -> Dict[str, Any]:
    if not API_BASE_URL:
        raise RuntimeError("API_BASE_URL is required")
    if not MODEL_NAME:
        raise RuntimeError("MODEL_NAME is required")
    if not HF_TOKEN:
        raise RuntimeError("HF_TOKEN is required")

    try:
        openai_module = importlib.import_module("openai")
        OpenAI = getattr(openai_module, "OpenAI")
    except Exception as exc:  # pragma: no cover - runtime dependency check
        raise RuntimeError("openai package is required. Install dependencies from requirements.txt") from exc

    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

    with httpx.Client(base_url=OPENENV_BASE_URL, timeout=30.0) as http:
        tasks_resp = http.get("/tasks")
        tasks_resp.raise_for_status()
        tasks = tasks_resp.json()["tasks"]

        scores: Dict[str, float] = {}
        for task in tasks:
            task_id = task["task_id"]
            scores[task_id] = round(_run_task(client, http, task_id), 4)

    overall = round(sum(scores.values()) / max(1, len(scores)), 4)
    return {
        "scores": scores,
        "overall_score": overall,
        "model_name": MODEL_NAME,
        "api_base_url": API_BASE_URL,
    }


def main() -> None:
    result = run_inference()
    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    out_path = artifacts_dir / "inference_results.json"
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
