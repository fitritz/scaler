from __future__ import annotations

from src.env.baseline import run_baseline
from src.env.environment import SupportOpsEnv


def test_all_task_grader_scores_are_bounded() -> None:
    env = SupportOpsEnv()
    tasks = env.tasks()["tasks"]

    assert len(tasks) >= 3

    for task in tasks:
        env.reset(task["task_id"])
        score = env.grader()["score"]
        assert 0.0 <= score <= 1.0


def test_baseline_returns_all_tasks() -> None:
    results = run_baseline()
    assert "scores" in results
    assert len(results["scores"]) >= 3
    assert 0.0 <= results["overall_score"] <= 1.0
