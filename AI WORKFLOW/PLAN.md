# PLAN.md

## Purpose
This file is the living implementation plan. It reflects the current intended direction of the project and the concrete next steps for Agent-ACP integration.

---

## Project Summary
OpenClaude is a local-first agent runtime with a rich internal execution model: dynamic prompt assembly, typed tools, permissions, hooks, memory, transcripts, tasks, subagents, and provider abstraction. The next major objective is to expose that runtime cleanly through ACP so that IDE clients can drive it with near-full fidelity instead of only a basic prompt bridge.

---

## Current Baseline
Today the repository has a working ACP bridge, but it is still a thin compatibility layer.

What currently works:
- ACP initialization, session creation, prompt forwarding, cancellation, model switching, and permission requests.
- Basic session modes exposed to JetBrains.
- Tool call and thought/message streaming from the headless OpenClaude process into ACP updates.
- Multi-provider model catalog selection through bridge environment variables.
- Project instruction loading now includes `AI WORKFLOW/{AGENTS,PLAN,PROGRESS,NEXT_TASKS}.md` in the same memory path as `CLAUDE.md`.

What is still missing for full integration:
- ACP config options as the primary control surface.
- A formal two-axis session model for capacity profile plus workflow role.
- Persistent ACP session list/load/title metadata across process lifetimes.
- Advertised ACP slash commands and runtime command synchronization.
- ACP-side workflow policy that matches the real tool/permission model.
- A sanitized ACP JSON profile set in `ACP/ACP-JSONS`.
- A verification matrix for all mode combinations before broad tool testing.

---

## ACP And Agent Synthesis

### ACP-side conclusions from `ACP/*.md`
- `configOptions` should be the primary session control surface; legacy `modes` should be kept in sync only for compatibility.
- ACP sessions should expose not only prompt handling, but also session metadata, command availability, plans, tool updates, and configuration changes.
- Session control should be modeled as stateful protocol data, not hidden in prompt text.
- Slash commands are advertised via `available_commands_update`, but still run through standard prompt turns.
- Tool calls, permission requests, plans, terminals, and file locations are first-class UX concepts in ACP and should be mapped explicitly.

### Agent-side conclusions from `docs_en/*.md`
- The runtime already has the internal primitives needed for richer ACP integration: prompt orchestration, typed tools, permission modes, session persistence, memory, commands, tasks, subagents, and verification-oriented workflows.
- The current gap is not lack of agent capability. The gap is the ACP contract surface that exposes those capabilities coherently.
- Context management is central. Any ACP session design must account for token budget, compaction behavior, transcript replay, and mode-specific prompt restrictions.
- Tool behavior and safety should be enforced in the runtime, not only implied by mode names.

---

## Target Agent-ACP Workflow

### Design Goal
Reach a "full integration" state where ACP clients can drive the real OpenClaude runtime with explicit, inspectable session controls rather than relying on a minimally adapted headless CLI loop.

### Primary Session Dimensions

#### 1. Capacity Profile
Two operating session profiles:
- `LOW`: intended for 32k-token-class backbones.
- `HIGH`: intended for 128k-token-class backbones.

These profiles should govern:
- prompt assembly aggressiveness
- transcript replay depth
- attachment loading
- compaction thresholds
- tool result truncation policy
- plan verbosity
- verification depth defaults

#### 2. Workflow Role
Four workflow roles:
- `ASK`: consultant/specification elicitation layer; no code or document edits.
- `PLAN`: manager/architect layer; no code edits; may create/update/append Markdown files only.
- `FIX`: tester/debugger layer; prioritize verification and bug fixing; defer substantial refactors to later iterations and document them.
- `CODE`: implementation layer; code and document changes allowed, with transparent reporting of all changes.

### ACP Representation Strategy
The target ACP contract should expose these controls in three ways:

1. `configOptions` as the primary control surface
- `context_profile`: `low | high`
- `workflow_mode`: `ask | plan | fix | code`
- `model`: provider-specific model selector
- `brave_mode`: `off | on` for ACP confirmations on mutating actions

2. ACP `modes` for workflow compatibility
- Expose the four workflow roles directly:
  - `ask`
  - `plan`
  - `fix`
  - `code`
- Continue accepting legacy combined identifiers such as `low_code` during bridge parsing so older persisted state can still load safely.

3. Advertised slash commands
- `/low`, `/high`
- `/ask`, `/plan`, `/fix`, `/code`
- `/brave`, `/careful`
- Optional combined shortcuts later if useful: `/low-ask`, `/high-code`

4. Dedicated ACP executables when useful
- `openclaude-acp-low`
- `openclaude-acp-high`
- These wrappers let ACP JSON templates pin a default capacity profile at process start while still allowing explicit in-session switching through config options or slash commands.

This keeps the ACP client surface aligned to the user-facing workflow names while preserving bridge-side backward compatibility and providing a cleaner LOW/HIGH deployment story.

---

## Mode Policy Matrix

| Workflow | Editing Policy | Tool Policy | Output Policy |
|----------|----------------|-------------|---------------|
| `ASK` | No file edits | Read/search/fetch only; no shell writes | Clarify requirements, produce analysis/spec notes in chat only |
| `PLAN` | Markdown-only edits | Read/search/fetch and Markdown file writes/edits only | Produce concrete plan artifacts in `.md` files and ACP plan updates |
| `FIX` | Code edits allowed only for bounded fixes | Full verification-oriented tool access, testing first | Run tests, isolate defects, fix safe issues, defer large rewrites to documented backlog |
| `CODE` | Code and doc edits allowed | Full normal tool access with standard permission policy | Implement requested changes and report modifications transparently |

### Capacity Profile Policy

| Profile | Context Strategy | Planning Strategy | Verification Strategy |
|---------|------------------|-------------------|-----------------------|
| `LOW` | Aggressive context budgeting, smaller transcript replay, earlier compaction | Concise plans and summaries | Focused verification with bounded artifacts |
| `HIGH` | Richer transcript/context replay, larger attachments, slower compaction | More detailed plans and broader state retention | Deeper verification and broader evidence capture |

---

## Agent-ACP Architecture Target

### Session Control Plane
- ACP config options become the canonical session state.
- Legacy ACP modes mirror the combined config state for older clients.
- Slash commands update the same underlying session state instead of introducing a separate branch of logic.

### Prompt Construction Plane
- Capacity profile and workflow role both feed prompt assembly.
- Workflow role changes system instructions, tool exposure, and permission defaults.
- Capacity profile changes context budget, transcript replay, and compaction behavior.
- Platform also feeds prompt assembly: Windows sessions should steer toward PowerShell behavior, Linux sessions toward Bash behavior.

### Execution Plane
- Tool gating should be derived from workflow role, not only from a coarse ACP mode.
- ACP tool call updates should eventually carry richer locations, diffs, and terminal embeddings where available.
- FIX mode should default to a verification-first loop before edit-heavy behavior.
- FIX/CODE mutating actions should be confirmation-first by default in JetBrains ACP, with an explicit `brave` override that bypasses confirmations but not workflow restrictions.

### Session Persistence Plane
- ACP sessions should persist enough metadata for `session/list`, `session/load`, and session titles to work across process restarts.
- Resume should reconstruct workflow role, capacity profile, model, and relevant session metadata.

### UX Plane
- ACP clients should see current configuration, available slash commands, plan updates, tool progress, permission prompts, and session metadata updates without guessing.
- ACP failures should degrade into a final assistant message with a concrete explanation, not an abrupt transport/runtime stop.

---

## ACP-JSON Configuration Strategy

### Source Of Truth
ACP client configurations live in `ACP/ACP-JSONS`.

### Configuration Rules
- Keep checked-in ACP JSON files sanitized; never store live API keys.
- Use environment placeholders or documented variable names only.
- Separate profiles by provider and by intended workflow when useful.

### Planned ACP JSON Templates
Planned future files:
- `agent-openrouter-low.json`
- `agent-openrouter-high.json`
- `agent-openai-low.json`
- `agent-openai-high.json`
- `agent-huggingface-low.json`
- `agent-huggingface-high.json`
- `agent-local-openai-low.json`
- `agent-local-openai-high.json`
- `agent-ollama-low.json`
- `agent-ollama-high.json`

Each template should document:
- executable path
- repo root
- provider base URL
- model defaults
- bridge env vars for capacity/workflow controls
- safe placeholder key usage

---

## Implementation Roadmap

### Iteration 1: Foundation And Local Tooling (Complete)
Goal: Establish local execution with Ollama and core tool set.

Subtasks:
- [x] Initial CLI runtime and prompt loop.
- [x] Integration with Ollama via OpenAI-compatible API.
- [x] Core tools (Bash, FileRead, FileEdit, Glob, Grep).

---

### Iteration 2: Provider Abstraction And Health (Complete)
Goal: Support multiple providers and add diagnostics.

Subtasks:
- [x] OpenAI and OpenRouter provider profiles.
- [x] `doctor:runtime` and `doctor:report` diagnostic system.
- [x] ACP bridge for JetBrains IDE integration.

---

### Iteration 3: SDK Decoupling And Protocol Stability (In Progress)
Goal: Remove Anthropic SDK dependency from the shared runtime.

Subtasks:
- [x] Update `WebFetchTool` to remove Anthropic domain preflight.
- [ ] Define provider-neutral tool/content block types.
- [ ] Update `src/Tool.ts` and shared message plumbing to use local types.
- [ ] Replace Anthropic SDK abort error dependency in `src/utils/errors.ts`.
- [ ] Migrate deferred tools (FileRead, Bash, etc.) to new protocol types.
- [ ] Remove or generalize remaining ant-only helper assumptions that block open-provider runtime paths.

---

### Iteration 4: v2.0 Multi-Provider And Cross-Platform (Active)
Goal: Expand LLM provider support and provide Linux executables.

Subtasks:
- [x] Expand ACP bridge to support multiple models.
- [ ] Add support for HuggingFace API and Local OpenAI providers.
- [x] Create Linux executables (CLI and ACP Bridge).
- [x] Comprehensive documentation of all 47+ tools and 4 ACP modes.
- [x] Update README.md with "Zero to 100" setup guide for PyCharm.

---

### Iteration 5: Agent-ACP Full Integration Design (Complete)
Goal: Produce the target operating model and implementation roadmap before broad ACP tool testing.

Subtasks:
- [x] Read all ACP protocol docs in `ACP/*.md`.
- [x] Read all agent runtime docs in `docs_en/*.md`.
- [x] Define the dual-axis session model: `LOW/HIGH` plus `ASK/PLAN/FIX/CODE`.
- [x] Decide on ACP `configOptions` as the primary control surface with legacy mode fallback.
- [x] Define the ACP JSON profile strategy for `ACP/ACP-JSONS`.
- [x] Document the staged implementation roadmap and verification matrix.

---

### Iteration 6: Agent-ACP Full Integration Implementation (Complete)
Goal: Implement the protocol-facing control plane and persistence model in small, verifiable batches.

Subtasks:
- [x] Add ACP session config options for context profile, workflow mode, and model.
- [x] Keep ACP workflow modes synchronized with the config option state.
- [x] Advertise ACP slash commands and connect them to the same session state model.
- [x] Persist ACP sessions so `session/list`, `session/load`, titles, and metadata survive process restarts.
- [x] Map workflow roles to real tool gating and permission policy.
- [x] Add ACP JSON templates in `ACP/ACP-JSONS` with sanitized placeholders only.
- [x] Add a verification matrix for all `LOW/HIGH x ASK/PLAN/FIX/CODE` combinations.

---

### Iteration 7: Agent-ACP Mode And Provider Corrections (Complete)
Goal: Resolve the first real-client integration gaps found after the initial rollout.

Subtasks:
- [x] Replace deprecated HuggingFace `api-inference` base URLs with `router.huggingface.co`.
- [x] Change the ACP mode surface to expose only `ask`, `plan`, `fix`, and `code`.
- [x] Preserve backward compatibility by continuing to accept combined legacy mode IDs during parsing.
- [x] Add dedicated LOW/HIGH ACP wrapper entrypoints and executable build commands.
- [x] Repoint ACP JSON templates to the dedicated LOW/HIGH executables where appropriate.

---

### Iteration 8: Agent-ACP Verification And Hardening (Planned)
Goal: Execute the verification matrix, validate real JetBrains behavior, and harden workflow restrictions based on observed client behavior.

Subtasks:
- [ ] Execute the Agent-ACP verification matrix across all profile/workflow combinations.
- [ ] Validate JetBrains behavior for ACP `configOptions` versus legacy `modes`.
- [ ] Refine FIX and PLAN enforcement based on observed tool-call behavior.
- [ ] Verify persistent session list/load behavior across bridge restarts.
- [ ] Test sanitized ACP JSON templates against real provider environments.
- [ ] Resume HuggingFace and Local OpenAI runtime support hardening where gaps remain.
- [x] Bake `AI WORKFLOW` repository control docs into runtime instruction loading when present.
- [x] Audit `docs_en/*.md` features against the current codebase and feed the gaps back into the roadmap.
- [x] Add a `brave` ACP control for confirmation bypass while keeping workflow-role restrictions intact.
- [x] Improve FIX/CODE ACP permission prompts so mutating actions include clearer change previews.
- [x] Align the HuggingFace ACP templates with the requested Router model and token style.
- [x] Make the ACP bridge launcher path and shell guidance platform-aware for Windows vs Linux.
- [x] Convert bridge/runtime early-stop paths into user-visible ACP responses instead of silent mid-turn failures.

---

## Verification Matrix For Full Integration
Before broad tool testing is considered complete, verify at least:

### Session control
- `context_profile` can switch between `low` and `high`.
- `workflow_mode` can switch between `ask`, `plan`, `fix`, and `code`.
- Legacy ACP mode changes keep config options in sync.
- Slash commands keep config options and legacy modes in sync.

### Workflow policy
- ASK prevents all edits.
- PLAN only permits Markdown edits.
- FIX defaults to verification-first behavior and documents deferred large fixes.
- CODE permits normal implementation behavior.

### Persistence
- Session list survives bridge restarts.
- Session load restores title, model, context profile, workflow mode, and transcript.
- Session metadata updates appear in ACP clients.

### UX parity
- Available slash commands are advertised.
- Plan updates stream during planning workflows.
- Tool calls, permissions, and cancellations remain coherent under every workflow mode.

### Provider coverage
- OpenRouter
- OpenAI
- HuggingFace
- Ollama
- Local OpenAI-compatible server

---

## Current Focus
Current active iteration: Iteration 8 in progress.

Current objective:
- Enter final testing with the bridge/runtime hardening in place, then use live JetBrains custom-agent validation to confirm the integrated behavior end to end.

---

## Risks / Open Questions
- JetBrains ACP client support for newer config option UX must be verified against the current plugin behavior; legacy modes may remain necessary longer than expected.
- The current bridge is still process-local for session memory, so persistent session semantics may require a storage layer instead of in-memory state.
- LOW/HIGH should govern context policy, not only model labels; the exact budget tuning will need empirical adjustment.
- LOW/HIGH currently influence prompt policy and session semantics more than deep runtime token budgeting; more concrete context-policy tuning is still needed.
- FIX mode boundaries must be strict enough to avoid unplanned refactors while still allowing bounded repairs.
- ACP JSON templates must be sanitized because the existing sample file currently contains a live-style secret and should not be used as a checked-in pattern.
- The runtime still has Anthropic SDK and ant-only assumptions in some shared code paths, so "provider-neutral" remains partially complete rather than finished.

---

## Deferred / Later Ideas
- Auto-generate ACP JSON profile templates from a single declarative matrix.
- Auto-generate the README tool inventory from `src/tools.ts` and build flags.
