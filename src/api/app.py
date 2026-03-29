from __future__ import annotations

from fastapi import FastAPI, HTTPException

from src.env.baseline import run_baseline
from src.env.environment import SupportOpsEnv
from src.env.models import Action

app = FastAPI(title="Women Safety OpenEnv", version="0.1.0")
env = SupportOpsEnv()


@app.get("/")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "womens-safety-openenv"}


@app.post("/reset")
def reset(task_id: str = "easy_incident_triage") -> dict:
    try:
        return env.reset(task_id).model_dump()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/step")
def step(action: Action) -> dict:
    try:
        return env.step(action).model_dump()
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/state")
def state() -> dict:
    return env.state()


@app.get("/tasks")
def tasks() -> dict:
    return env.tasks()


@app.get("/grader")
def grader() -> dict:
    try:
        return env.grader()
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/baseline")
def baseline() -> dict:
    return run_baseline()
