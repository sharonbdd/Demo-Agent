# PROGRESS.md

## Current Status
- Current iteration: Iteration 8 (Agent-ACP verification and hardening)
- Current focus: final JetBrains custom-agent testing and real IDEA MCP validation against the hardened cross-platform ACP bridge
- Overall state: the ACP bridge is now platform-aware for Windows/Linux launch behavior, returns user-visible explanations on early-stop paths, has confirmation-first FIX/CODE behavior with a `brave` override, and passes the local bridge/template/e2e test suite; the remaining work is live JetBrains/provider validation and only the minimum Anthropic decoupling still required for non-Anthropic backends
- Last updated after: Iteration 8 cross-platform launcher hardening and non-abrupt failure handling

---

## What Currently Works
- Multi-provider runtime support through the OpenAI-compatible path.
- Interactive CLI/TUI loop with session persistence on the runtime side.
- Typed tools with permission-gated execution.
- Runtime diagnostics via `doctor:runtime`.
- A working ACP bridge that supports initialization, prompt turns, cancellation, permission prompts, model switching, and basic session modes.

---

## Completed Work
- [x] Initial CLI agent loop.
- [x] Local provider profile system (`profile:init`, `dev:profile`).
- [x] OpenAI-compatible shim for Ollama/OpenRouter.
- [x] Runtime health checks (`doctor:runtime`) and report generation (`doctor:report`).
- [x] ACP bridge implementation (`scripts/openclaude_acp_bridge.py`).
- [x] `WebFetchTool` update: removed Anthropic preflight endpoint.
- [x] README "Zero to 100" PyCharm setup guide aligned to the actual ACP flow.
- [x] Tool capability inventory added with availability/status buckets sourced from `src/tools.ts` and `scripts/build.ts`.
- [x] ACP bridge model picker made provider-aware and configurable via `OPENCLAUDE_MODEL_PROVIDER`, `OPENCLAUDE_ACP_MODELS`, and `OPENCLAUDE_EXTRA_MODELS`.
- [x] Linux CLI and ACP build commands documented.
- [x] Read all ACP protocol docs in `ACP/*.md` for an ACP-side deep dive.
- [x] Read all runtime docs in `docs_en/*.md` for an agent-side deep dive.
- [x] Produced a comprehensive Agent-ACP integration plan centered on `LOW/HIGH` profiles and `ASK/PLAN/FIX/CODE` workflow roles.
- [x] Updated workflow documents to use the new Agent-ACP plan as the source of truth.
- [x] Added ACP session config options for `context_profile`, `workflow_mode`, and `model`.
- [x] Synchronized legacy ACP modes to the new dual-axis session model.
- [x] Added ACP slash command advertisement and prompt-time slash-command state switching.
- [x] Added persistent ACP session metadata storage for list/load/title continuity across bridge restarts.
- [x] Added workflow-aware tool gating for ASK and PLAN modes in the ACP bridge permission path.
- [x] Created sanitized ACP JSON templates for OpenRouter, OpenAI, HuggingFace, Ollama, and local OpenAI-compatible providers.
- [x] Added a checked-in Agent-ACP verification matrix.
- [x] Corrected ACP mode exposure to publish only `ask`, `plan`, `fix`, and `code` while still accepting legacy combined IDs during parsing.
- [x] Switched HuggingFace ACP templates and docs from `api-inference.huggingface.co` to `router.huggingface.co`.
- [x] Added dedicated LOW/HIGH ACP wrapper entrypoints and built Windows executables for them.
- [x] Repointed LOW/HIGH ACP JSON templates to the dedicated profile executables.
- [x] Added ACP bridge unit tests covering mode/config synchronization, workflow gating, session persistence reload, and four-mode exposure.
- [x] Fixed ASK workflow launcher tool whitelisting so `AskUserQuestion` is allowed consistently in both the runtime tool list and permission gate.
- [x] Sanitized `ACP/ACP-JSONS/old.json` and aligned it to the current repo path and compatibility executable.
- [x] Added ACP JSON template tests covering provider/profile matrix coverage, dedicated LOW/HIGH executable usage, and placeholder-only credential hygiene.
- [x] Rebuilt `dist/cli.mjs`, `dist/openclaude-acp-low.exe`, `dist/openclaude-acp-high.exe`, and `dist/openclaude-acp-modes.exe`.
- [x] Added ACP protocol end-to-end tests for rebuilt executables, session controls, slash-command state changes, and restart persistence.
- [x] Added a tool registry audit covering the default open build, env-gated open-repo tools, and checked-in IDEA MCP allowlist expectations.
- [x] Documented the current verification run in `ACP/ACP-JSONS/VERIFICATION_RESULTS.md`.
- [x] Extended project instruction loading so `AI WORKFLOW/AGENTS.md`, `PLAN.md`, `PROGRESS.md`, and `NEXT_TASKS.md` are injected automatically when present.
- [x] Added a Bun regression test covering `AI WORKFLOW` memory-file detection and ordered instruction loading.
- [x] Audited `docs_en/*.md` against the current codebase and recorded capability/gap status in `docs_en/FEATURE_AUDIT.md`.
- [x] Fixed Windows ACP bridge session serialization so live `asyncio` subprocess handles are never sent through `dataclasses.asdict()`.
- [x] Rebuilt `dist/openclaude-acp-low.exe`, `dist/openclaude-acp-high.exe`, and `dist/openclaude-acp-modes.exe` after the ACP serialization fix.
- [x] Added a regression test to ensure `SessionState.to_json()` ignores live process handles.
- [x] Added a `brave_mode` ACP config option plus `/brave` and `/careful` slash commands.
- [x] Made FIX/CODE mutating actions confirmation-first by default in ACP, with clearer permission preview titles and a `brave` bypass that preserves workflow restrictions.
- [x] Added provider-auth env normalization so HuggingFace `HF_TOKEN` and OpenRouter `OPEN_ROUTER_KEY` are mapped to `OPENAI_API_KEY` for the spawned runtime.
- [x] Updated HuggingFace ACP templates to use `Qwen/Qwen3-Coder-Next-FP8:together` on Router with `HF_TOKEN`.
- [x] Added bridge/template regression coverage for brave mode, provider auth env normalization, and change-preview permission titles.
- [x] Rebuilt `dist/openclaude-acp-modes.exe` and `dist/openclaude-acp-high.exe` after the brave/confirmation hardening changes.
- [x] Built `dist/openclaude-acp-low-updated.exe` as a replacement artifact because `dist/openclaude-acp-low.exe` was locked by a running JetBrains process during rebuild.
- [x] Made ACP launcher selection platform-aware so Windows uses the `.cmd` launcher path while Linux uses the POSIX `bin/openclaude` entrypoint.
- [x] Added platform-specific shell guidance to ACP session policy so Windows sessions prefer PowerShell and Linux sessions prefer Bash.
- [x] Converted prompt-time launch/session/runtime failures into final ACP assistant messages instead of abrupt internal stops.
- [x] Added regression coverage for platform-aware command building and user-visible error responses.
- [x] Built `dist/openclaude-acp-high-updated.exe` as a replacement artifact because `dist/openclaude-acp-high.exe` was locked by a running process during rebuild.
- [x] Re-ran the combined ACP bridge/template/e2e suite successfully after the cross-platform and failure-handling changes (`35 passed`).
- [x] Added a provider-agnostic fallback that converts XML-style raw tool-call text (for example `<function=Bash>...</function>`) into real `tool_use` blocks before the query loop executes tools.
- [x] Added Bun regression coverage for the raw tool-call fallback parser.
- [x] Built `dist/openclaude-acp-low-v2.exe` as an additional LOW replacement artifact because `dist/openclaude-acp-low-updated.exe` was locked during the latest rebuild.

---

## Important Decisions

### [Anthropic SDK Decoupling]
- Context: Core protocol types are still imported from the Anthropic SDK in shared runtime paths.
- Decision: Continue migrating to local, provider-neutral types.
- Impact: Keeps the runtime provider-agnostic and simplifies future ACP and OpenAI-compatible integration.

### [ACP Control Surface]
- Context: ACP now prefers session config options over dedicated modes, but the JetBrains UX should still show the user-facing workflow roles directly.
- Decision: Use ACP `configOptions` as the primary session control surface and expose only `ask`, `plan`, `fix`, and `code` as ACP modes, while still accepting older combined mode IDs during parsing.
- Impact: The client-visible mode list now matches the intended workflow model without losing backward compatibility for stored or cached mode identifiers.

### [Dual-Axis Session Model]
- Context: The desired workflow has two dimensions: token-budget profile and engineering role.
- Decision: Model sessions using capacity profile (`LOW/HIGH`) plus workflow role (`ASK/PLAN/FIX/CODE`).
- Impact: Makes mode semantics explicit and lets context policy and tool policy evolve independently.

### [Workflow Role Enforcement]
- Context: Mode names alone are not enough unless they map to actual runtime restrictions.
- Decision: ASK, PLAN, FIX, and CODE will be implemented as explicit tool and permission policies, not just prompt text.
- Impact: ACP sessions can enforce consultant/architect/tester/developer behavior in a verifiable way.

### [ACP JSON Hygiene]
- Context: The existing ACP sample config includes a live-style secret value, which is unsafe as a checked-in pattern.
- Decision: Future ACP JSON files in `ACP/ACP-JSONS/` must be sanitized and use placeholders or env-based values only.
- Impact: Prevents accidental secret leakage and gives users reusable config templates.

### [ACP Session State Model]
- Context: The original bridge kept only in-memory session state and exposed a single coarse mode concept.
- Decision: Persist ACP session metadata to disk and model session state as `context_profile + workflow_mode + model`, with config options as the primary interface, workflow-only ACP modes, and dedicated LOW/HIGH wrappers for deployment convenience.
- Impact: ACP clients can list/load richer sessions, show cleaner mode names, and launch profile-pinned agents without embedding LOW/HIGH into the visible mode names.

### [LOW/HIGH Executable Split]
- Context: Different ACP presets often want a fixed default capacity profile, and the generic bridge executable was locked by an active JetBrains process during upgrade.
- Decision: Add `openclaude-acp-low` and `openclaude-acp-high` wrapper entrypoints and point LOW/HIGH ACP JSON templates at those binaries.
- Impact: ACP templates can now pin the intended profile at launch time, and upgrades no longer depend on replacing a single locked executable.

### [Local ACP Verification Coverage]
- Context: Iteration 8 requires verification, but live JetBrains/provider runs are slower and harder to repeat than bridge-local checks.
- Decision: Add Python test coverage for ACP bridge behavior and ACP JSON template integrity, and fix any mismatches those checks expose immediately.
- Impact: Core ACP control-plane behavior and checked-in ACP preset hygiene are now regression-tested locally before live IDE/provider verification.

### [Provider Prompt Blocker]
- Context: Real OpenRouter and HuggingFace ACP prompt turns were attempted after the binary rebuild using local credentials/configuration.
- Decision: Record those live attempts as blocked by an ACP/runtime `RequestError: Internal error` until the underlying prompt execution path is debugged.
- Impact: Provider-template launch verification is complete, but real provider prompt execution is not yet healthy enough to mark the provider-validation batch done.

### [JetBrains MCP Verification Boundary]
- Context: A live PyCharm process and ACP config are present locally, but the repo's JetBrains plugin detection does not find the JetBrains plugin installation.
- Decision: Treat checked-in IDEA MCP config validation as complete, but keep real IDEA MCP tool execution blocked until plugin installation/detection is resolved.
- Impact: Local static/config verification is done; full IDE-backed MCP tool verification remains an external integration task.

### [AI WORKFLOW Runtime Integration]
- Context: This repo now uses `AI WORKFLOW/{AGENTS,PLAN,PROGRESS,NEXT_TASKS}.md` as the source-of-truth operating workflow, but the runtime previously only auto-loaded `CLAUDE.md`-style instruction files.
- Decision: Extend the existing project-memory loader so those four `AI WORKFLOW` files are treated as ordered project instructions whenever they exist.
- Impact: The runtime now bakes in the repository workflow automatically without introducing a separate prompt-assembly path.

### [Windows ACP Serialization Fix]
- Context: ACP sessions launched from the packaged Windows bridge could fail during session persistence with `cannot pickle '_OverlappedFuture' object`.
- Decision: Stop using `dataclasses.asdict()` for `SessionState` persistence and serialize only the explicit JSON-safe fields, excluding the live `asyncio.subprocess.Process`.
- Impact: Packaged ACP presets such as the OpenRouter and HuggingFace LOW/HIGH configs can initialize without crashing on Windows due to process-handle serialization.

### [Confirmation-First FIX/CODE Policy]
- Context: In JetBrains ACP, `fix` and `code` should surface a preview and request confirmation before mutating actions unless the user explicitly chooses a more permissive mode.
- Decision: Add a persisted `brave` session flag exposed through ACP config and slash commands; when OFF, mutating actions in allowed workflows continue through ACP permission prompts with clearer previews; when ON, confirmations are bypassed without weakening workflow-role tool restrictions.
- Impact: JetBrains ACP sessions now have a safer default editing posture while still allowing an explicit fast path for trusted flows.

### [JetBrains Plugin Clarification]
- Context: The intended deployment surface is the installed JetBrains AI plugin configured via `acp.json`, not a custom standalone plugin for this repo.
- Decision: Treat that plugin path as the primary real-client validation target and keep repo changes focused on ACP compatibility, config UX, and IDEA MCP interoperability.
- Impact: Future validation work should focus on the existing JetBrains AI custom-agent flow rather than searching for a separate plugin installation.

### [Platform-Aware ACP Launch And Shell Guidance]
- Context: The bridge previously hardcoded a Windows `.cmd` launch path and generic shell behavior, which breaks Linux launch behavior and can mislead Windows sessions into using Bash-oriented terminal actions.
- Decision: Make launcher selection platform-aware and inject explicit Windows-vs-Linux shell guidance into the ACP session policy.
- Impact: Windows and Linux now have separate launch behavior, and the model is steered toward PowerShell on Windows and Bash on Linux.

### [User-Visible Early Stop Handling]
- Context: Launch failures and other early-stop paths could terminate a turn with an internal error instead of a useful explanation to the user.
- Decision: Convert those bridge/runtime failures into final ACP assistant messages with the reason, platform, and recent stderr tail when available.
- Impact: The user now gets a proper end-of-turn explanation instead of a dead or half-finished session.

### [Raw Tool-Call Text Fallback]
- Context: Some OpenAI-compatible providers can emit tool intent as XML-style text instead of structured `tool_use` blocks, which leaks raw `<function=...>` markup into the user-visible answer and stops tool execution.
- Decision: Detect text-only XML-style function markup and synthesize a real `tool_use` block before the standard query/tool execution loop runs.
- Impact: The runtime can now recover from that provider behavior instead of exposing raw tool markup to the user.

---

## Known Gaps / Issues
- JetBrains ACP client behavior for `configOptions` still needs live verification.
- FIX workflow is currently guided mainly by prompt policy; its bounded-repair behavior still needs empirical verification.
- PLAN workflow currently enforces Markdown edits by bridge-side tool gating, but should be validated against real tool-call edge cases.
- FIX workflow still relies mostly on prompt policy for "bounded repair" behavior; only ASK/PLAN restrictions are strongly enforced in the bridge today.
- HuggingFace Router and Local OpenAI runtime support still need broader end-to-end verification beyond the ACP template layer.
- The old `dist\\openclaude-acp-modes.exe` remains a compatibility path, but the primary deployment target is now the dedicated `openclaude-acp-low` and `openclaude-acp-high` executables.
- Existing legacy Python tests in the repo still depend on missing async pytest support and currently do not provide a clean whole-suite signal.
- JetBrains ACP client behavior still cannot be fully validated from local unit tests; those checks require real IDE interaction.
- Real ACP prompt turns currently fail with `RequestError: Internal error` in both tested remote-provider environments (OpenRouter and HuggingFace), so provider execution still needs debugging.
- The local `~/.jetbrains/acp.json` contains a live HuggingFace key and is not sanitized; this is outside the repo but relevant operationally.
- Shared runtime paths still include Anthropic SDK type imports and some ant-only assumptions, so the provider-neutralization work is not complete yet.
- Real-provider prompt behavior should be re-checked after the Windows bridge rebuild, because the prior startup failure path overlapped with session-persistence code in the packaged ACP bridge.
- `dist\\openclaude-acp-low.exe` could not be replaced during the latest rebuild because a running JetBrains process locked the file; `dist\\openclaude-acp-low-updated.exe` contains the latest code until the lock is released.
- `dist\\openclaude-acp-high.exe` was also locked during the latest rebuild; `dist\\openclaude-acp-high-updated.exe` contains the latest code until that lock is released.
- `dist\\openclaude-acp-low-updated.exe` was locked during the latest rebuild; `dist\\openclaude-acp-low-v2.exe` is the current LOW replacement artifact with the latest raw-tool-call fallback fix.

---

## Iteration Log

### Iteration 1 - Foundation
Planned:
- Core CLI runtime and prompt loop.
- Ollama integration via local API.
- Basic file and shell tools.

Completed:
- CLI loop with `src/main.tsx` and `src/QueryEngine.ts`.
- Shell and file tools implemented in `src/services/tools/`.

---

### Iteration 2 - Provider And Health
Planned:
- Add OpenAI and OpenRouter support.
- Add runtime diagnostics and reports.
- Implement JetBrains ACP bridge.

Completed:
- Provider profiles system and `dev:profile` command.
- `doctor:runtime` and `doctor:report` tools.
- Working ACP bridge executable flow for JetBrains integration.

---

### Iteration 3 - SDK Decoupling
Planned:
- Decouple `WebFetchTool`.
- Define local protocol and type definitions.
- Update `src/Tool.ts` and shared message plumbing.
- Replace SDK abort error dependency in `src/utils/errors.ts`.

Completed:
- `WebFetchTool` removal of Anthropic preflight.

Notes:
- This remains a prerequisite for deeper provider-neutral runtime work.

---

### Iteration 4 - v2.0 Multi-Provider And Cross-Platform
Planned:
- Expand ACP bridge model support.
- Add HuggingFace and local OpenAI support.
- Create Linux executables.
- Improve README and tool documentation.

Completed:
- ACP bridge model selection expanded and made configurable.
- Linux build path documented.
- README setup and tool inventory improved.

Notes:
- This iteration improved usability, but not full ACP protocol fidelity.

---

### Iteration 5 - Agent-ACP Full Integration Design
Planned:
- Deep-dive the ACP protocol docs.
- Deep-dive the agent runtime docs.
- Define a complete Agent-ACP workflow for `LOW/HIGH` and `ASK/PLAN/FIX/CODE`.
- Update workflow planning docs only, with no runtime code changes.

Completed:
- ACP documentation review completed.
- Agent runtime documentation review completed.
- Comprehensive Agent-ACP plan documented in `PLAN.md`.
- `AGENTS.md`, `NEXT_TASKS.md`, and `PROGRESS.md` updated to align with the new integration roadmap.

Notes:
- No runtime code or ACP JSON files were changed in this iteration by design.

---

### Iteration 6 - Agent-ACP Full Integration Implementation
Planned:
- Implement ACP config options and compatibility modes.
- Add ACP slash commands and persistent session metadata.
- Enforce workflow-aware restrictions in the bridge.
- Create sanitized ACP JSON templates and a verification matrix.

Completed:
- ACP config options implemented for context profile, workflow mode, and model.
- Legacy mode compatibility implemented with flattened `low_*` and `high_*` mode IDs.
- ACP slash commands advertised and wired into prompt-time session updates.
- Persistent ACP session state implemented for list/load/title continuity.
- ASK and PLAN bridge-side tool gating implemented.
- Sanitized ACP JSON templates created for the main provider profiles.
- Verification matrix added under `ACP/ACP-JSONS/VERIFICATION_MATRIX.md`.

Notes:
- This iteration implemented the control plane; the next batch should focus on executing and documenting real-client verification.

---

### Iteration 7 - Agent-ACP Mode And Provider Corrections
Planned:
- Correct the ACP mode list to show `ask`, `plan`, `fix`, and `code`.
- Fix the deprecated HuggingFace endpoint in ACP templates and docs.
- Introduce dedicated LOW/HIGH bridge executables and wire templates to them.

Completed:
- ACP modes now publish only the four workflow roles.
- Legacy combined IDs remain accepted during bridge parsing for backward compatibility.
- HuggingFace templates and README examples now use `https://router.huggingface.co/v1`.
- Added `scripts/openclaude_acp_low.py` and `scripts/openclaude_acp_high.py`.
- Built `dist/openclaude-acp-low.exe` and `dist/openclaude-acp-high.exe`.
- Updated LOW/HIGH ACP JSON templates to target the dedicated executables.
- Aligned the README build, setup, and mode documentation to the dedicated LOW/HIGH executable flow and the `ask`/`plan`/`fix`/`code` ACP mode surface.

Notes:
- The previous `openclaude-acp-modes.exe` remains optional for compatibility, but the dedicated LOW/HIGH binaries are now the documented primary path.

---

### Iteration 8 - Agent-ACP Verification And Hardening
Planned:
- Execute the verification matrix against the corrected four-mode ACP surface.
- Validate live JetBrains behavior and provider presets.
- Refine workflow restrictions where real usage exposes mismatches.

Completed so far:
- Added `test_openclaude_acp_bridge.py` to verify config/mode synchronization, workflow gating, session persistence reload, and four-mode exposure.
- Fixed ASK-mode tool launch configuration so `AskUserQuestion` is available consistently.
- Added `test_acp_json_templates.py` to validate template coverage, dedicated executable wiring, and placeholder-only credentials.
- Sanitized the legacy `ACP/ACP-JSONS/old.json` sample so no checked-in ACP JSON contains a live-style secret.
- Rebuilt the Windows ACP executables and the CLI artifact.
- Added `test_acp_protocol_e2e.py` to exercise the rebuilt executables over real ACP stdio, including restart persistence and slash-command updates.
- Added `test_tool_registry_audit.py` to verify the open-build tool registry and IDEA MCP config expectations.
- Executed live ACP prompt attempts against local OpenRouter and HuggingFace configurations; both currently fail with `RequestError: Internal error`.
- Extended `src/utils/claudemd.ts` so `AI WORKFLOW/*.md` files are loaded as project instructions in the existing memory pipeline.
- Added `src/utils/claudemd.ai-workflow.test.ts` to lock the new loader behavior down.
- Added `docs_en/FEATURE_AUDIT.md` to map the runtime wiki to current implementation status and remaining provider-neutralization gaps.
- Fixed `scripts/openclaude_acp_bridge.py` session serialization to avoid touching the live `active_process` field.
- Rebuilt the Windows ACP executables and re-ran ACP protocol verification successfully after that fix.
- Added a persisted brave-mode control and improved ACP permission previews for mutating actions.
- Updated HuggingFace Router templates to your requested Qwen model and token style.
- Rebuilt the packaged bridge artifacts where file locks allowed and re-ran the ACP bridge/template/e2e suites successfully.
- Added platform-aware launcher selection and shell guidance.
- Added user-visible ACP responses for launch/runtime early-stop scenarios.
- Added a fallback parser for XML-style raw tool-call text and rebuilt replacement binaries for live retesting.

Notes:
- Local ACP bridge, ACP JSON, and tool-registry verification are now in place. The remaining blockers are real provider prompt execution, JetBrains plugin/MCP availability, and any FIX-mode behavior issues found once live prompt turns succeed.
