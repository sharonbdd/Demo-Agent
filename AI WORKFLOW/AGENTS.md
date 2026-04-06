# AGENTS.md

## Purpose
This repository is developed using an iterative AI-agent workflow. The agent should make steady, minimal, testable progress in small iterations while preserving project continuity across sessions.

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

If the repository contains `AI WORKFLOW/AGENTS.md`, `AI WORKFLOW/PLAN.md`, `AI WORKFLOW/PROGRESS.md`, and `AI WORKFLOW/NEXT_TASKS.md`, the runtime should treat them as project instruction files in addition to normal `CLAUDE.md` behavior.

---

## Agent Working Rules

1. Think Before Coding
- Do not assume unclear requirements; state assumptions explicitly.
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
- Do not refactor, reformat, or improve unrelated code.
- Match the existing code style and patterns.
- If unrelated issues are found, mention them but do not fix them.
- Clean up only what your changes affect.
- Every code change must directly trace back to the task.

4. Goal-Driven Execution
- Translate tasks into clear, testable success criteria.
- When applicable:
  1. [Step] -> verify: [check]
  2. [Step] -> verify: [check]
  3. [Step] -> verify: [check]
- Do not stop at partial completion; ensure the goal is fully met and verified.

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
- relevant tests are added or updated when appropriate
- relevant docs and status files are updated

---

## Project Overview
### Project Name
Demo-Agent: OpenClaude

### Goal
A full-featured AI agent runtime that provides a local, provider-agnostic interface for file operations, terminal commands, and coding workflows. The current product objective is full Agent-ACP integration with broader provider support and cross-platform execution.

### Primary User / Use Case
Developers and automation engineers who need a local-first agent capable of complex, tool-driven tasks across providers and IDE-integrated ACP workflows.

### Success Criteria
- Reliable tool execution with permission-gated hooks.
- Provider-agnostic runtime that works with local and remote OpenAI-compatible providers.
- Minimal dependency on proprietary SDKs in shared protocol layers.
- Robust local health checks and diagnostics.
- ACP integration that exposes real session controls, persistence, slash commands, plans, and workflow-safe tool policies.

---

## Technical Context
### Stack
- Runtime: TypeScript, Bun, Node.js
- CLI/TUI: Interactive terminal-based interface
- ACP bridge: Python
- AI Integration: Custom OpenAI-compatible shim, provider-specific implementations
- Verification: `doctor:runtime`, `smoke`, `hardening`, and future ACP verification matrix

### Important Paths
- App code: `src/`
- Tool implementations: `src/services/tools/`, `src/tools/`
- Core loop: `src/QueryEngine.ts`, `src/query.ts`
- Agent runtime docs: `docs_en/`
- ACP protocol docs and ACP JSON configs: `ACP/`, `ACP/ACP-JSONS/`
- Workflow control docs: `AI WORKFLOW/`

---

## Agent-ACP Planning Rules
- Before doing ACP integration work or ACP tool testing, read the ACP protocol docs in `ACP/*.md` and the runtime docs in `docs_en/*.md`.
- Use `docs_en/FEATURE_AUDIT.md` as the current capability/gap summary after the runtime-doc review.
- Treat `ACP/ACP-JSONS/` as the home for checked-in ACP client configuration templates.
- Never store live secrets in checked-in ACP JSON files. Use placeholders or environment-variable-based values only.
- Prefer ACP `configOptions` as the primary session UX surface. Keep legacy `modes` in sync for compatibility when required.
- Keep the Agent-ACP design aligned to the real runtime architecture described in `docs_en/`; do not create a separate fake control model only for the bridge.
- Treat the installed JetBrains AI plugin plus `acp.json` as the intended integration surface for this project.

---

## Required Session Model For Agent-ACP

### Capacity Profiles
- `LOW`: intended for 32k-token-class models.
- `HIGH`: intended for 128k-token-class models.

### Workflow Roles
- `ASK`: consultant/specification elicitation; must not edit code or documents.
- `PLAN`: manager/architect; may only create, update, or append Markdown files.
- `FIX`: tester/debugger; performs comprehensive testing and bounded fixes; large fixes must be deferred and documented.
- `CODE`: software developer/programmer; may edit code and documents and must report changes transparently.

### ACP Control Surfaces
- Primary: session config options
- Compatibility: ACP workflow modes, with bridge-side parsing support for older combined mode IDs when needed
- Operator UX: advertised slash commands
- Deployment option: dedicated LOW/HIGH ACP executables for profile-pinned presets

---

## Planning-Only Iterations
If an iteration explicitly says planning only:
- do not change runtime code
- do not change ACP bridge behavior
- do not add or edit ACP JSON configs unless the task explicitly asks for config-file planning artifacts
- only update planning and status documents

---

## Architecture / Design Constraints
- Maintain provider abstraction via the OpenAI-compatible shim.
- Ensure all tool executions remain permission-gated.
- Favor local models for privacy and low latency where practical.
- Minimize direct dependencies on proprietary SDKs in shared protocol layers.
- Preserve existing Claude Code capabilities where they still work with non-Anthropic backends; generalize or simplify only the Anthropic-dependent pieces that block your target setup.
- When an Anthropic-dependent capability can be replaced by JetBrains IDEA MCP or JetBrains ACP-native UX, prefer that replacement over deeper Anthropic-specific coupling.
- Detect platform correctly in ACP/runtime flows: Windows sessions should prefer PowerShell-oriented terminal behavior, Linux sessions should prefer Bash-oriented terminal behavior.
- In early-stop or failure scenarios, return a user-visible explanation through ACP instead of terminating the turn silently or mid-response.
- Ensure Windows and PowerShell compatibility for operational workflows.
- Ensure Linux remains a first-class target alongside Windows, especially for CLI and ACP bridge packaging.
- Keep ACP integration faithful to the real agent runtime instead of flattening behavior into prompt-only hacks.

---

## Coding Preferences
- Use TypeScript for the core runtime.
- Maintain consistency with the existing TUI and interactive style.
- Prefer minimal, testable patches over large rewrites.
- Document new ACP workflows and tool policies in repository docs as they are implemented.

---

## Non-Goals
- Do not make the product dependent on Anthropic proprietary or paid access.
- Do not bypass the runtime permission model just to simplify ACP integration.
