# 25 High-Value Development Skills for OpenClaude

This list is optimized for programming, coding, debugging, refactoring, testing, review, and delivery workflows. Each skill is a reusable workflow built from one or more repo tools.

## 1. Repo Recon
- Purpose: Understand an unfamiliar codebase quickly.
- Tools: `FileReadTool`, `GlobTool`, `GrepTool`, `ToolSearchTool`, `BriefTool`
- Workflow: find entrypoints, inspect architecture files, trace config, summarize hotspots.
- Best for: first-pass onboarding and feature triage.

## 2. Bug Reproduction Triage
- Purpose: turn a vague bug report into a concrete failure path.
- Tools: `BashTool`, `PowerShellTool`, `FileReadTool`, `TodoWriteTool`
- Workflow: run app/tests, capture error, identify repro steps, record hypotheses.
- Best for: flaky issues, startup failures, CI-only failures.

## 3. Stack Trace to Root Cause
- Purpose: map an exception or crash to the responsible code path.
- Tools: `GrepTool`, `FileReadTool`, `LSPTool`, `BriefTool`
- Workflow: trace frames, inspect call chain, identify the state invariant that broke.
- Best for: backend exceptions and frontend runtime errors.

## 4. Safe Single-File Refactor
- Purpose: make a focused code change with low regression risk.
- Tools: `FileReadTool`, `FileEditTool`, `FileWriteTool`
- Workflow: inspect current logic, patch minimally, preserve style and nearby patterns.
- Best for: small fixes and local cleanup.

## 5. Cross-File Refactor
- Purpose: update multiple modules consistently.
- Tools: `GlobTool`, `GrepTool`, `FileReadTool`, `FileEditTool`, `TodoWriteTool`
- Workflow: locate all call sites, patch in dependency order, track remaining updates.
- Best for: API renames, signature changes, config schema changes.

## 6. Test-First Fix
- Purpose: lock in a bug before changing implementation.
- Tools: `FileReadTool`, `GlobTool`, `GrepTool`, `FileEditTool`, `BashTool`
- Workflow: find test suite, add failing test, implement fix, rerun tests.
- Best for: regressions and bug-proofing.

## 7. Minimal Regression Sweep
- Purpose: verify the smallest useful set of checks after a change.
- Tools: `BashTool`, `PowerShellTool`, `BriefTool`, `TodoWriteTool`
- Workflow: run targeted tests, lint, typecheck, summarize what passed and what remains unverified.
- Best for: fast iteration.

## 8. Dead Code Detection
- Purpose: identify likely-unused files, exports, and branches.
- Tools: `GlobTool`, `GrepTool`, `LSPTool`, `BriefTool`
- Workflow: search references, inspect entrypoints, flag unreachable or orphaned code.
- Best for: cleanup and dependency reduction.

## 9. Config and Env Audit
- Purpose: understand runtime configuration and environment assumptions.
- Tools: `GlobTool`, `GrepTool`, `FileReadTool`, `ConfigTool`
- Workflow: locate env reads, defaults, config files, and mismatch points.
- Best for: deployment bugs and local setup issues.

## 10. Logging and Observability Patch
- Purpose: add high-signal diagnostics without noisy instrumentation.
- Tools: `FileReadTool`, `FileEditTool`, `BashTool`
- Workflow: inspect current logging style, add targeted logs/guards, verify output path.
- Best for: hard-to-reproduce runtime issues.

## 11. CLI Workflow Builder
- Purpose: create or improve scripts and command workflows.
- Tools: `BashTool`, `PowerShellTool`, `FileEditTool`, `WorkflowTool`
- Workflow: inspect existing scripts, add new command path, validate arguments and output.
- Best for: dev tooling and automation.

## 12. API Contract Review
- Purpose: verify a client-server or module boundary contract.
- Tools: `FileReadTool`, `GrepTool`, `LSPTool`, `BriefTool`
- Workflow: inspect types, payload shapes, response handling, and error paths.
- Best for: integration bugs and breaking changes.

## 13. Dependency Upgrade Impact Scan
- Purpose: estimate change risk before or after upgrading a library.
- Tools: `GrepTool`, `GlobTool`, `FileReadTool`, `WebFetchTool`
- Workflow: find usages, inspect wrappers, compare assumptions with docs or changelog.
- Best for: package bumps and migration planning.

## 14. Failing Test Cluster Analysis
- Purpose: group multiple failing tests into one or two root causes.
- Tools: `BashTool`, `GrepTool`, `FileReadTool`, `TodoWriteTool`
- Workflow: run failing subset, cluster symptoms, trace shared code path, propose fix order.
- Best for: broken branches and CI red builds.

## 15. Frontend Runtime Debugger
- Purpose: debug component behavior, props flow, and state transitions.
- Tools: `FileReadTool`, `GrepTool`, `LSPTool`, `WebBrowserTool`
- Workflow: inspect component tree, trace events, reason about rendering and side effects.
- Best for: React or UI state bugs.

## 16. Backend Request Path Tracer
- Purpose: trace a request from entrypoint through business logic to persistence.
- Tools: `GrepTool`, `FileReadTool`, `LSPTool`, `BriefTool`
- Workflow: find route, service, validation, storage, and error mapping layers.
- Best for: API bugs and performance bottlenecks.

## 17. Persistence/Schema Change Planner
- Purpose: plan a DB or schema change with caller impact in mind.
- Tools: `GlobTool`, `GrepTool`, `FileReadTool`, `EnterPlanModeTool`, `ExitPlanModeV2Tool`
- Workflow: inspect models and consumers, sequence migration, compat layer, and rollout.
- Best for: migrations and stored-data changes.

## 18. PR Review Assistant
- Purpose: review a diff for bugs, regressions, and missing tests.
- Tools: `FileReadTool`, `GrepTool`, `BriefTool`, `AgentTool`
- Workflow: inspect changed files, reason about edge cases, summarize findings by severity.
- Best for: code review and pre-merge risk checking.

## 19. Documentation Drift Checker
- Purpose: compare docs, READMEs, and setup instructions against actual code.
- Tools: `FileReadTool`, `GrepTool`, `WebFetchTool`, `BriefTool`
- Workflow: inspect docs, verify commands and flags, list stale claims.
- Best for: onboarding quality and release prep.

## 20. MCP Integration Explorer
- Purpose: understand what external MCP servers expose and how to use them.
- Tools: `ListMcpResourcesTool`, `ReadMcpResourceTool`, `MCPTool`, `BriefTool`
- Workflow: enumerate resources, inspect schemas or docs, test useful operations.
- Best for: connected IDE, GitHub, issue tracker, or custom backend integrations.

## 21. Multi-Agent Parallel Investigation
- Purpose: split a broad problem into parallel sub-investigations.
- Tools: `AgentTool`, `SendMessageTool`, `TaskOutputTool`, `TaskStopTool`
- Workflow: delegate focused tracks, collect results, consolidate into one action plan.
- Best for: large incidents and broad refactors.

## 22. Worktree Isolation Workflow
- Purpose: keep risky or parallel efforts isolated.
- Tools: `EnterWorktreeTool`, `ExitWorktreeTool`, `BashTool`, `TodoWriteTool`
- Workflow: switch into isolated worktree, perform scoped changes, summarize result before exit.
- Best for: experimental fixes and side-by-side feature work.

## 23. Scheduled Maintenance or Follow-Up
- Purpose: set reminders or delayed prompts for later validation.
- Tools: `CronCreateTool`, `CronListTool`, `CronDeleteTool`, `SleepTool`
- Workflow: schedule follow-up checks, list active automations, clean stale entries.
- Best for: release follow-ups and deferred checks.

## 24. Structured Output Generator
- Purpose: produce machine-readable results for downstream automation.
- Tools: `SyntheticOutputTool`, `BriefTool`, `FileWriteTool`
- Workflow: validate required schema, emit normalized JSON, optionally persist artifact.
- Best for: CI summaries, release notes payloads, generated metadata.

## 25. Skill-Driven Domain Specialist
- Purpose: route specialized tasks into reusable playbooks.
- Tools: `SkillTool`, `ToolSearchTool`, `FileReadTool`, `AgentTool`
- Workflow: discover the right skill, apply it with minimal context, escalate to sub-agent if needed.
- Best for: repeated workflows like migrations, reviews, releases, and framework-specific work.

# Suggested Top 10 Default Skill Pack

If you want the most generally useful subset first, start with:
1. Repo Recon
2. Bug Reproduction Triage
3. Stack Trace to Root Cause
4. Safe Single-File Refactor
5. Cross-File Refactor
6. Test-First Fix
7. Minimal Regression Sweep
8. PR Review Assistant
9. Multi-Agent Parallel Investigation
10. MCP Integration Explorer

# Good Skill Folder Names

Use these if you want to turn the list into actual Codex skills:
- `repo-recon`
- `bug-repro-triage`
- `stack-trace-root-cause`
- `safe-single-file-refactor`
- `cross-file-refactor`
- `test-first-fix`
- `minimal-regression-sweep`
- `dead-code-detection`
- `config-env-audit`
- `logging-observability-patch`
- `cli-workflow-builder`
- `api-contract-review`
- `dependency-upgrade-impact-scan`
- `failing-test-cluster-analysis`
- `frontend-runtime-debugger`
- `backend-request-path-tracer`
- `schema-change-planner`
- `pr-review-assistant`
- `documentation-drift-checker`
- `mcp-integration-explorer`
- `multi-agent-parallel-investigation`
- `worktree-isolation-workflow`
- `scheduled-maintenance-followup`
- `structured-output-generator`
- `skill-driven-domain-specialist`