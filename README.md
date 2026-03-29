# Women Safety OpenEnv - Round 1 Submission Guide

This repository contains a complete OpenEnv environment for Round 1 of the OpenEnv Hackathon.

Primary implementation in this repo is a women safety incident-response simulation.

If you are collaborating in a team, read this file once end-to-end before coding.

## 1) Problem Statement, In Plain Language

You must build an environment where an AI agent can learn by interacting through three standard methods:

1. `reset()`
2. `step(action)`
3. `state()`

The environment must represent a real human workflow, include at least three tasks of increasing difficulty, provide deterministic grading from 0.0 to 1.0, and support reproducible baseline inference.

## 2) What "Real-World" Means Here

A valid domain is a workflow people actually do in industry or operations. In this repo, the workflow is women safety incident operations:

1. assess incident risk
2. set priority
3. assign responders
4. escalate to authorities when needed
5. close case while following safety policy

This is not a toy game. Decisions mimic real operational constraints (quality, speed, compliance).

## 3) OpenEnv Terms Explained (Detailed)

# 3.1 Observation

What the agent can see at each step.

Examples in this project:

1. current incident fields
2. queue context
3. policy-related metadata
4. step count and progress signals

### 3.2 Action

What the agent is allowed to do at each step.

Examples in this project:

1. assess risk
2. set priority
3. assign responder
4. escalate to authorities
5. close case

### 3.3 Reward

Numerical feedback after every action.

Good environments use dense reward (partial credit), not only final pass/fail.

### 3.4 `reset()`

Starts a new episode and returns the initial observation for a selected task.

### 3.5 `step(action)`

Advances the environment by one action and returns:

1. next observation
2. reward
3. done flag
4. info dictionary

### 3.6 `state()`

Returns full current internal state for debugging/evaluation visibility.

### 3.7 Task

A concrete objective with clear success criteria.

Required: at least 3 tasks, typically easy -> medium -> hard.

### 3.8 Grader

Programmatic scoring logic for each task episode.

Must be deterministic and bounded in [0.0, 1.0].

### 3.9 Baseline Inference

A script that runs a fixed agent strategy/model setup and reports reproducible scores.

For hackathon compliance, a root-level `inference.py` is expected.

### 3.10 OpenEnv Metadata (`openenv.yaml`)

Describes environment identity, API endpoints, model references, and task listing.

## 4) Hackathon Requirements -> How This Repo Maps

1. Real-world environment: implemented (women safety incident operations)
2. Full OpenEnv interface: implemented via typed models and API
3. Minimum 3 tasks: implemented (`easy_incident_triage`, `dispatch_queue_management`, `high_risk_safe_resolution`)
4. Deterministic graders in [0.0, 1.0]: implemented
5. Reward function with partial progress: implemented
6. Baseline scoring script: implemented in `scripts/run_baseline.py`
7. Dockerized deployment: implemented via `Dockerfile`
8. API endpoints for evaluator: implemented

Note for final submission rules: add root `inference.py` that uses OpenAI client with `API_BASE_URL`, `MODEL_NAME`, and `HF_TOKEN`.

## 5) Repository Layout

1. `src/env/`: environment core (`models.py`, `environment.py`, `tasks.py`, `rewards.py`, `graders.py`, `baseline.py`)
2. `src/api/`: FastAPI application and route handlers
3. `scripts/`: helper scripts for baseline run and local validation
4. `tests/`: API, environment spec, and grader tests
5. `artifacts/`: generated outputs (example baseline results)
6. `openenv.yaml`: OpenEnv metadata and endpoint/task declaration
7. `Dockerfile`: container runtime

## 6) Current Tasks and Difficulty

1. `easy_incident_triage` (easy): correct risk, priority, responder mapping
2. `dispatch_queue_management` (medium): manage multiple incidents with resource constraints
3. `high_risk_safe_resolution` (hard): complete safe resolution under escalation and policy constraints

Each task has deterministic grading, and final score is always clamped to [0.0, 1.0].

## 7) API Contract (Evaluator-Facing)

1. `POST /reset?task_id=<task_id>`
2. `POST /step`
3. `GET /state`
4. `GET /tasks`
5. `GET /grader`
6. `GET /baseline`

## 8) Setup (Windows)

### 8.1 Clone

```bash
git clone <YOUR_REPO_URL>
cd scaler
```

### 8.2 Create and activate venv

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 8.3 Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 8.4 Start server

```bash
uvicorn src.api.app:app --reload --port 7860
```

Server URL:uvicorn src.api.app:app --reload --port 7860

```text
http://127.0.0.1:7860
```

### 8.5 Quick sanity checks

```bash
curl -X POST "http://127.0.0.1:7860/reset?task_id=easy_incident_triage"
curl "http://127.0.0.1:7860/tasks"
curl "http://127.0.0.1:7860/state"
curl "http://127.0.0.1:7860/baseline"
```

## 9) Tests and Local Validation

Run unit tests:

```bash
python -m pytest -q
```

Run baseline script:

```bash
python scripts/run_baseline.py
```

Expected output file:

```text
artifacts/baseline_results.json
```

Run local pre-submission validator:

```bash
python scripts/validate_submission.py
```

## 10) Docker and Deployment

Build:

```bash
docker build -t womens-safety-openenv .
```

Run:

```bash
docker run -p 7860:7860 womens-safety-openenv
```

For HF Space deployment, ensure health and `/reset` return 200.

## 11) Mandatory Submission Variables (Inference)

Define these in your environment/secrets:

1. `API_BASE_URL`
2. `MODEL_NAME`
3. `HF_TOKEN`

For compatibility, many teams also support optional fallback `API_KEY`.

## 12) Team Collaboration Guide (Important)

### 12.1 Branch Strategy

1. `main`: always stable
2. `feature/<short-name>`: each task/feature
3. `fix/<short-name>`: bug fixes

### 12.2 Daily Team Flow

1. Pull latest `main`
2. Create/update feature branch
3. Make small focused commits
4. Run tests and validator locally
5. Open PR with clear summary and evidence

### 12.3 Commit Message Style

Use consistent prefixes:

1. `feat:` new feature
2. `fix:` bug fix
3. `test:` tests
4. `docs:` docs changes
5. `refactor:` structural cleanup

Examples:

```text
feat: add deterministic grader for hard task
fix: clamp grader scores to 0-1 range
docs: expand README with submission checklist
```

### 12.4 PR Checklist for Teammates

1. Description is clear and scoped
2. Tests pass locally
3. Validator passes locally
4. No unrelated file changes
5. Reviewer can reproduce using commands in this README

### 12.5 Suggested Team Roles

1. Environment owner: task and transition logic
2. Grader owner: deterministic scoring and edge cases
3. API owner: endpoint contract and schema stability
4. Infra owner: Docker and HF deployment
5. QA owner: tests, validation, reproducibility

## 13) Women Safety Task Design

Deterministic grading dimensions in this implementation:

1. risk assessment correctness
2. escalation correctness
3. policy-safe guidance
4. response efficiency

Implemented tasks:

1. easy: single incident triage
2. medium: multi-incident dispatch
3. hard: high-risk policy-safe resolution

## 14) Disqualification Risks to Avoid

1. environment not deployable
2. `/reset` failing on deployed URL
3. missing or non-working baseline inference
4. graders returning constant score
5. fewer than 3 tasks
6. non-deterministic or out-of-range grader outputs

## 15) Final Pre-Submission Checklist

1. HF Space ping works
2. `/reset` returns HTTP 200
3. Docker build succeeds
4. `openenv.yaml` valid and complete
5. typed models + `reset/step/state` behave correctly
6. 3+ tasks with deterministic graders in [0.0, 1.0]
7. root-level `inference.py` present and runs
8. runtime under 20 minutes on 2 vCPU / 8 GB memory
9. README accurately reflects current implementation

## 16) License

MIT
