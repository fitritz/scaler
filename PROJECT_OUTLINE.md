# Project Outline - OpenEnv Hackathon (Round 1)

## 1. Project Snapshot

- Project name: SupportOps Arena
- One-line summary: An OpenEnv environment for AI agents to triage, prioritize, and resolve customer support tickets with real operational constraints.
- Problem statement: Current support workflows are noisy and time-sensitive; agents need realistic training/evaluation for routing, response quality, and SLA compliance.
- Target users: Agent researchers, LLM evaluation teams, and support automation startups.
- Success metric for Round 1: Pass all validation gates and achieve strong baseline score progression across easy, medium, and hard tasks.

## 2. Why This Can Win

- Real-world utility: Support ticket triage is a genuine business workflow, not a toy domain.
- Strong grader potential: Deterministic checks for routing correctness, SLA handling, policy compliance, and resolution quality.
- Good reward shaping: Partial credit at each step (classification, priority, escalation, resolution) with penalties for bad actions.
- Clear novelty: Multi-objective support operations simulation (speed, quality, compliance, customer sentiment).

## 3. OpenEnv Compliance Plan

- Implement typed Pydantic models:
  - Observation model: ticket queue snapshot, SLA timers, agent workload, policy flags, customer sentiment.
  - Action model: classify_ticket, set_priority, assign_team, request_info, draft_reply, escalate, resolve.
  - Reward model: scalar reward, component breakdown, policy_violation flags.
- Implement API:
  - reset() returns initial observation.
  - step(action) returns observation, reward, done, info.
  - state() returns full internal state for debugging and evaluator use.
- Add openenv.yaml with metadata, task listing, action schema references, and endpoint config.
- Validate with openenv validate in CI before every push.

## 4. Task Design (Easy -> Medium -> Hard)

### Task 1 (Easy): Single-Ticket Correct Triage

- Objective: Classify one incoming ticket and assign correct priority/team.
- Success criteria: Correct category + priority + team assignment.
- Grader score:
  - 1.0 if all three are correct.
  - 0.66 if two are correct.
  - 0.33 if one is correct.
  - 0.0 if none are correct.

### Task 2 (Medium): Multi-Ticket Queue Management

- Objective: Process a queue of tickets while meeting SLA constraints.
- Success criteria: Maximize number of correctly triaged tickets before SLA breaches.
- Grader score: Weighted average of triage accuracy and SLA compliance.

### Task 3 (Hard): End-to-End Resolution Under Policy Constraints

- Objective: Resolve complex tickets requiring clarification, escalation, and policy-safe response drafting.
- Success criteria: Correct escalation decisions, policy-safe messaging, and successful final resolution.
- Grader score: Weighted blend of resolution success, policy compliance, and interaction efficiency.

## 5. Reward Function Design

- Dense partial rewards:
  - +0.2 for correct classification.
  - +0.2 for correct priority.
  - +0.2 for correct team assignment.
  - +0.2 for policy-safe response action.
  - +0.2 for successful final resolution.
- Penalties:
  - -0.1 for redundant/no-op actions.
  - -0.2 for incorrect escalation.
  - -0.3 for policy violation.
  - -0.05 per unnecessary step beyond threshold.
- Episode end conditions:
  - All tickets resolved.
  - Max steps reached.
  - Critical policy violation threshold crossed.

## 6. Required Endpoints

- /tasks: Returns all tasks and action schema requirements.
- /grader: Returns final grader score for completed episode.
- /baseline: Runs baseline inference and returns scores for all tasks.

## 7. Baseline Inference Script Plan

- File: scripts/run_baseline.py
- Uses OPENAI_API_KEY from environment variables.
- Runs fixed seeded episodes for reproducibility.
- Outputs per-task score and overall average.
- Saves baseline artifacts to artifacts/baseline_results.json.

## 8. Tech Decisions

- Language: Python 3.11+
- Core: OpenEnv + FastAPI
- Validation/models: Pydantic v2
- Testing: pytest
- Packaging: Docker
- Deployment: Hugging Face Spaces (Docker SDK, tagged openenv)

## 9. Repo Structure

- openenv.yaml
- Dockerfile
- README.md
- src/
  - env/
    - models.py
    - environment.py
    - rewards.py
    - tasks.py
    - graders.py
  - api/
    - app.py
    - routes.py
- scripts/
  - run_baseline.py
  - validate_submission.py
- tests/
  - test_env_spec.py
  - test_tasks_graders.py
  - test_api_endpoints.py
- artifacts/

## 10. Timeline To Deadline

### Day 1

- Finalize task domain and schemas.
- Implement Observation/Action/Reward models.
- Implement reset(), step(), state() skeleton.

### Day 2

- Implement Task 1 and Task 2 logic.
- Add graders with deterministic scoring.
- Add dense reward shaping and episode boundaries.

### Day 3

- Implement Task 3 hard scenario.
- Build /tasks, /grader, /baseline endpoints.
- Write baseline inference script.

### Day 4

- Dockerize and test docker build + docker run.
- Deploy to HF Space and verify ping/reset flow.
- Run openenv validate and fix all issues.

### Day 5

- Complete README with architecture and scores.
- Add tests and run full regression.
- Dry-run pre-submission checklist.

## 11. Pre-Submission Checklist (Must Pass)

- [ ] HF Space deploys and responds.
- [ ] openenv validate passes.
- [ ] Docker image builds and runs.
- [ ] Baseline script runs without error.
- [ ] At least 3 tasks with deterministic graders.
- [ ] Grader scores are always in 0.0 to 1.0 range.
- [ ] README includes setup, spaces, task definitions, and baseline scores.

## 12. Risk Register

- Risk: Grader exploits or score hacking.
  - Mitigation: Deterministic checks + hidden edge cases + anti-shortcut constraints.
- Risk: Sparse reward leads to unstable baseline.
  - Mitigation: Dense rewards with intermediate signals and step penalties.
- Risk: Deployment/runtime mismatch on HF.
  - Mitigation: Reproduce container locally and pin dependencies.
- Risk: Failing validator late.
  - Mitigation: Add validate step in local script and CI from day 1.

## 13. Next Build Steps

1. Scaffold repository structure and placeholder files.
2. Implement environment core and typed models.
3. Implement three tasks and graders.
4. Add API endpoints and baseline script.
5. Add tests + Docker + HF deployment.
6. Run full validation and submit.
