# docs_en Feature Audit

This file maps the `docs_en/` runtime wiki to the current codebase and the remaining generalization work for a provider-neutral, JetBrains-friendly agent runtime.

## Audit Summary

The current repository already satisfies most of the runtime capabilities described in `docs_en/`: prompt orchestration, typed tools, permissions, memory, session persistence, commands, context management, tasks, bridge operation, and settings all exist in the TypeScript runtime today.

The main gaps are not missing agent features. The main gaps are:

- Anthropic-specific shared types and code paths still remain in core runtime modules.
- Some ant-only runtime hooks still assume Anthropic-specific implementations.
- Live JetBrains IDEA MCP execution has not yet been fully verified end to end.
- Real remote-provider ACP prompt execution currently fails before the broader ACP tool matrix can be completed.

## Feature Matrix

| Doc | Capability Areas | Current Status | Notes / Gaps |
|---|---|---|---|
| `00-product-overview.md` | Full agent runtime, dynamic context, governed tools, persistence, extensibility | Implemented | Matches current architecture well. |
| `01-system-prompt-and-orchestration.md` | Prompt assembly, mode instructions, extension-driven prompt sections | Implemented | `CLAUDE.md` memory path exists; this iteration also loads `AI WORKFLOW/*.md` as project instructions. |
| `02-tools-permissions-and-execution.md` | Typed tools, execution pipeline, permissions, hooks | Implemented | Broad local audit exists; full live JetBrains MCP execution still pending. |
| `03-skills-plugins-mcp.md` | Skills, plugins, MCP servers/resources/tools | Implemented with external-validation gap | Local registry/config validation exists; live IDEA MCP tool execution remains blocked on plugin verification. |
| `04-memory-and-session.md` | Instruction memory, typed memory, transcript persistence, resume, compaction | Implemented | Project instruction loading is now extended to `AI WORKFLOW` source-of-truth files. |
| `05-commands-ui-and-operator-experience.md` | Slash commands, TUI state, operator feedback, headless/SDK paths | Implemented | ACP slash-command advertisement already exists; real IDE confirmation still pending. |
| `06-verification-and-quality.md` | Runtime diagnostics, verification loop, traceability | Implemented with known repo-wide gaps | Local ACP verification is strong; repo-wide `bun run typecheck` still has pre-existing failures. |
| `07-architecture-map.md` | Runtime map across entry, query, tools, permissions, memory, bridge, settings | Implemented | Accurate to current repo. |
| `08-agent-runtime-loop.md` | Startup, per-turn loop, recovery, tool execution loop | Implemented | No major gap found from this audit. |
| `09-message-model-and-state.md` | Message types, app/bootstrap/session state | Implemented with provider-neutrality gap | Shared state exists, but some message/protocol types still import Anthropic SDK definitions. |
| `10-context-management.md` | Cached prompt sections, selective loading, compaction, truncation | Implemented | LOW/HIGH context tuning still needs more empirical shaping. |
| `11-task-model.md` | Task types, state, lifecycle, polling/output | Implemented | Present in current runtime/task subsystem. |
| `12-workspace-and-isolation.md` | cwd/project-root/worktree model, permission-scoped FS access, session isolation | Implemented | Works today; Linux and IDE-backed validation should continue as part of cross-platform hardening. |
| `13-failure-recovery.md` | API/tool/permission/session/bridge failure handling | Implemented with active provider bug | ACP/provider prompt path currently hits `RequestError: Internal error` in live OpenRouter and HuggingFace runs. |
| `14-configuration-system.md` | Settings sources, validation, env gates, provider config | Implemented | Strong current system; more provider-neutral cleanup is still needed in shared runtime paths. |
| `15-mvp-scope.md` | Minimal rebuild guidance and phased architecture | Reference-only | Still useful as a simplification guide, not a missing-feature checklist. |
| `16-python-implementation-notes.md` | Python-port guidance | Reference-only | Helpful for bridge-side ideas, but production runtime remains TypeScript/Bun. |

## Future Plan Additions From This Audit

- Continue Iteration 3 provider-neutralization work in shared runtime paths:
  - replace Anthropic SDK message/content/tool types with local equivalents
  - remove Anthropic-specific abort/error/type imports from shared execution paths
  - generalize remaining ant-only model-resolution/runtime hooks where feasible
- Continue Iteration 8 external validation work:
  - debug the live ACP/provider prompt failure path
  - verify JetBrains plugin installation/detection
  - execute the real IDEA MCP tool matrix once prompt turns are healthy
- After external validation, tighten workflow-role enforcement where real ACP behavior exposes mismatches, especially for `FIX`.
