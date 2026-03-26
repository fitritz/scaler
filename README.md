# SupportOps Arena (OpenEnv)

This project is a hackathon submission environment where an AI agent learns customer support operations.

If you are new, read this file top to bottom once and you can run everything.

## What This Project Does

The environment simulates real support tickets. An agent must:

1. Classify each ticket.
2. Set correct priority.
3. Assign correct team.
4. Escalate when needed.
5. Resolve safely (without policy violations).

The project follows the OpenEnv format and provides:

1. `reset()`
2. `step(action)`
3. `state()`
4. Task grader and baseline score endpoints

## Who Should Use This

1. Teammates collaborating on the hackathon.
2. Anyone testing LLM/agent performance on real-world support workflows.
3. Reviewers who want deterministic task scoring from 0.0 to 1.0.

## Project Structure (Simple View)

1. `src/env/`: Environment logic (tasks, rewards, graders, models)
2. `src/api/`: FastAPI server and endpoints
3. `scripts/`: Baseline runner and validation script
4. `tests/`: Automated tests
5. `openenv.yaml`: OpenEnv metadata/config
6. `Dockerfile`: Container setup for deployment

## Tech Stack

1. Python 3.10+
2. FastAPI
3. Pydantic
4. Pytest
5. Docker

## Tasks Included

1. `easy_ticket_triage`
2. `queue_management`
3. `policy_safe_resolution`

All tasks are deterministic and have graders that return score in `[0.0, 1.0]`.

## API Endpoints

1. `POST /reset?task_id=<task_id>`
2. `POST /step`
3. `GET /state`
4. `GET /tasks`
5. `GET /grader`
6. `GET /baseline`

## Setup From Zero (Windows)

### Step 1: Clone the repo

```bash
git clone <YOUR_REPO_URL>
cd scaler
```

### Step 2: Create virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Step 3: Install dependencies

```bash
python -m pip install -r requirements.txt
```

### Step 4: Start API server

```bash
uvicorn src.api.app:app --reload --port 7860
```

Server should now be running at:
`http://127.0.0.1:7860`

## First Run Check (Copy/Paste)

Open a second terminal in project root and run:

```bash
curl -X POST "http://127.0.0.1:7860/reset?task_id=easy_ticket_triage"
curl "http://127.0.0.1:7860/tasks"
curl "http://127.0.0.1:7860/state"
curl "http://127.0.0.1:7860/baseline"
```

If you do not have `curl`, use browser for `GET` endpoints:

1. `http://127.0.0.1:7860/tasks`
2. `http://127.0.0.1:7860/state`
3. `http://127.0.0.1:7860/baseline`

## Run Tests

Use this command on Windows:

```bash
python -m pytest -q
```

## Run Baseline Script

```bash
python scripts/run_baseline.py
```

This creates:
`artifacts/baseline_results.json`

## Run Pre-Submission Validator

```bash
python scripts/validate_submission.py
```

## Docker Run

```bash
docker build -t supportops-arena .
docker run -p 7860:7860 supportops-arena
```

## How To Collaborate With Team

1. Create a branch:

```bash
git checkout -b feature/my-change
```

2. Commit your work:

```bash
git add .
git commit -m "add: short message"
```

3. Push branch:

```bash
git push -u origin feature/my-change
```

4. Open Pull Request to `main`.

## Common Issues

1. `pytest` not found:
   Use `python -m pytest -q` instead of `pytest -q`.

2. `ModuleNotFoundError: No module named src`:
   Run commands from project root folder, not from inside subfolders.

3. Port already in use:
   Start on another port:
   `uvicorn src.api.app:app --reload --port 7861`

## Hackathon Checklist (Quick)

1. 3 tasks exist (easy, medium, hard)
2. Graders output 0.0 to 1.0
3. `reset/step/state` work
4. `/tasks`, `/grader`, `/baseline` work
5. Docker builds
6. README is clear
7. Baseline script runs and outputs score

## License

MIT
