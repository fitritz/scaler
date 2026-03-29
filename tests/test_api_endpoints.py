from __future__ import annotations

from fastapi.testclient import TestClient

from src.api.app import app


client = TestClient(app)


def test_tasks_endpoint() -> None:
    response = client.get("/tasks")
    assert response.status_code == 200
    payload = response.json()
    assert "tasks" in payload
    assert len(payload["tasks"]) >= 3


def test_reset_and_state_endpoints() -> None:
    response = client.post("/reset", params={"task_id": "easy_incident_triage"})
    assert response.status_code == 200

    state_resp = client.get("/state")
    assert state_resp.status_code == 200
    assert state_resp.json()["initialized"] is True


def test_baseline_endpoint() -> None:
    response = client.get("/baseline")
    assert response.status_code == 200
    body = response.json()
    assert "overall_score" in body
