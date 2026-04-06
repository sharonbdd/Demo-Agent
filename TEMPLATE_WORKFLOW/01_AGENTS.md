# AGENTS.md

## Purpose
This repository is developed using an iterative AI-agent workflow. The agent should make steady, minimal, testable progress in small iterations, while preserving project continuity across sessions.

The agent must use the following files as the source of truth:
- `AGENTS.md` -> agent instructions, project requirements, constraints, and working rules
- `PLAN.md` -> current implementation plan, architecture, and iteration breakdown
- `PROGRESS.md` -> current project state, completed work, important decisions, and iteration history
- `NEXT_TASKS.md` -> the immediate next tasks to execute

---

## Development Workflow
The agent must follow this workflow on every work session:

1. Read `AGENTS.md`, `PLAN.md`, `PROGRESS.md`, and `NEXT_TASKS.md` before making changes.
2. Treat `NEXT_TASKS.md` as the active execution queue.
3. Implement only a small, coherent set of tasks in one iteration.
4. Prefer incremental, testable changes over large rewrites.
5. Preserve existing working behavior unless a task explicitly requires refactoring or breaking changes.
6. If requirements are unclear, infer the most reasonable implementation from the repository and documented plan.
7. After completing work:
   - update `PROGRESS.md`
   - mark finished items and decisions
   - update `NEXT_TASKS.md`
   - adjust `PLAN.md` only if the plan meaningfully changed
8. Keep documentation aligned with the codebase. Do not leave stale status notes.

---

## Agent Working Rules

1. Think Before Coding
- Do not assume unclear requirements — state assumptions explicitly.
- If ambiguity exists, present possible interpretations instead of silently choosing one.
- Ask for clarification when necessary rather than guessing.
- If a simpler or better approach exists, surface it.
- If confused, stop and clearly state what is unclear.
2. Simplicity First
- Implement the minimum code required to solve the problem.
- Do not add features, flexibility, or configurability that were not requested.
- Avoid abstractions for single-use code.
- Do not handle edge cases that are unrealistic or impossible.
- If a solution can be significantly simplified, simplify it.
- Prefer clarity and directness over clever or complex solutions.
3. Surgical Changes
- Only modify code directly related to the task.
- Do not refactor, reformat, or “improve” unrelated code.
- Match the existing code style and patterns.
- If unrelated issues are found, mention them but do not fix them.
- Clean up only what your changes affect (e.g., unused imports you introduced).
- Every code change must directly trace back to the task.
4. Goal-Driven Execution
- Translate tasks into clear, testable success criteria.
- When applicable:
  * Write or define tests first
  * Then implement until tests pass
  * For multi-step tasks, define a short plan:
    1. [Step] → verify: [check]
    2. [Step] → verify: [check]
    3. [Step] → verify: [check]
- Do not stop at partial completion — ensure the goal is fully met and verified.
5. General Execution Principles
- When adding code, also update related tests, types, docs, or configs if needed.
- If a task is large, complete the safest meaningful subset first.
- If multiple sub-tasks are independent, complete them in a logical order.
- Record important implementation decisions in `PROGRESS.md`.

---

## Definition of Done
A task is done only when all of the following are true:
- implementation is complete for the intended scope
- code is consistent with repository conventions
- obvious errors are resolved
- relevant tests are added/updated when appropriate
- relevant docs/status files are updated

---

## Project Overview
### Project Name
[Project name]

### Goal
[What this project is supposed to do]

### Primary User / Use Case
[Who uses it and for what]

### Success Criteria
- [Criterion 1]
- [Criterion 2]
- [Criterion 3]

---

## Technical Context
### Stack
- Frontend: [e.g. React, Next.js]
- Backend: [e.g. Node.js, FastAPI]
- Database: [e.g. PostgreSQL, SQLite]
- Testing: [e.g. Vitest, Pytest]
- Deployment: [e.g. Vercel, Docker]

### Important Paths
- App code: `[path]`
- Tests: `[path]`
- Config: `[path]`
- Docs: `[path]`

---

## Architecture / Design Constraints
- [Constraint 1]
- [Constraint 2]
- [Constraint 3]

Examples:
- Use server components by default unless client behavior is needed
- Keep business logic out of UI components
- Do not introduce new dependencies unless necessary
- Maintain backward compatibility for the API

---

## Coding Preferences
- [Preferred patterns]
- [Naming conventions]
- [Error handling preferences]
- [Testing expectations]

---

## Non-Goals
- [What should not be built right now]
- [Out-of-scope ideas to avoid]