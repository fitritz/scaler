from __future__ import annotations

import json
from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.env.baseline import run_baseline
from src.env.environment import SupportOpsEnv


REQUIRED_FILES = [
    "openenv.yaml",
    "Dockerfile",
    "README.md",
    "scripts/run_baseline.py",
]


def check_files() -> list[str]:
    missing = [path for path in REQUIRED_FILES if not Path(path).exists()]
    return missing


def check_openenv_yaml() -> list[str]:
    errors: list[str] = []
    path = Path("openenv.yaml")
    if not path.exists():
        return ["openenv.yaml missing"]

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    for key in ("name", "version", "api", "models", "tasks"):
        if key not in data:
            errors.append(f"openenv.yaml missing key: {key}")
    return errors


def check_tasks_and_graders() -> list[str]:
    errors: list[str] = []
    env = SupportOpsEnv()

    for task in env.tasks()["tasks"]:
        env.reset(task["task_id"])
        score = env.grader()["score"]
        if not (0.0 <= score <= 1.0):
            errors.append(f"score out of range for {task['task_id']}: {score}")

    return errors


def check_baseline() -> list[str]:
    errors: list[str] = []
    result = run_baseline()
    if "overall_score" not in result:
        errors.append("baseline did not return overall_score")
    if "scores" not in result or len(result["scores"]) < 3:
        errors.append("baseline must return scores for at least 3 tasks")
    return errors


def main() -> None:
    checks = {
        "missing_files": check_files(),
        "openenv_yaml": check_openenv_yaml(),
        "tasks_graders": check_tasks_and_graders(),
        "baseline": check_baseline(),
    }

    failed = {name: issues for name, issues in checks.items() if issues}

    print(json.dumps(checks, indent=2))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
