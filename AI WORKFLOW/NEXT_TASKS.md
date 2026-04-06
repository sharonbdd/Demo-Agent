# NEXT_TASKS.md

## Purpose
This file contains the immediate final-testing tasks for the Agent-ACP workstream.

---

## Active Tasks
1. Run final live JetBrains custom-agent validation through `acp.json`, especially OpenRouter/HuggingFace LOW/HIGH, using `dist\\openclaude-acp-low-v2.exe` and `dist\\openclaude-acp-high-updated.exe` if the in-place wrappers remain locked.
2. Validate JetBrains ACP client behavior for `context_profile`, `workflow_mode`, and `brave_mode`, plus `/low`, `/high`, `/ask`, `/plan`, `/fix`, `/code`, `/brave`, and `/careful`.
3. Execute the real IDE-backed verification matrix across all `LOW/HIGH x ASK/PLAN/FIX/CODE` combinations.
4. Verify real IDEA/JetBrains MCP tool execution through the installed JetBrains AI plugin custom-agent path.
5. If any provider prompt still fails, debug only the remaining runtime/provider issue after ruling out stale locked binaries.
6. Do only the minimum remaining Anthropic decoupling needed for non-Anthropic backends where JetBrains MCP or ACP-native behavior cannot replace the dependency.
7. Re-test the rebuilt Windows ACP executable in JetBrains against the original premature-stop scenario to confirm Windows `Bash` calls are recovered end to end through fallback parsing, runtime tool lookup, and the exposed tool list.

---

## Task Notes
- ACP `configOptions` are implemented and the ACP mode list now exposes only `ask`, `plan`, `fix`, and `code`.
- The session model remains two-dimensional: capacity profile (`LOW/HIGH`) plus workflow role (`ASK/PLAN/FIX/CODE`).
- Dedicated `openclaude-acp-low` and `openclaude-acp-high` executables are now the primary documented launch targets; `openclaude-acp-modes` is compatibility-only.
- Use `ACP/ACP-JSONS/VERIFICATION_MATRIX.md` as the source checklist for protocol validation.
- ACP JSON files must remain sanitized; never replace placeholders with live secrets in checked-in files.
- Local Python coverage now exists for config/mode synchronization, workflow gating, four-mode exposure, and persisted session reload behavior.
- ASK mode now exposes `AskUserQuestion` consistently in both launcher tool whitelisting and bridge-side permission gating.
- Local Python coverage now also validates ACP JSON template coverage, dedicated LOW/HIGH executable wiring, and placeholder-only credentials.
- Rebuilt binaries and ACP stdio verification are documented in `ACP/ACP-JSONS/VERIFICATION_RESULTS.md`.
- The checked-in IDEA MCP template expectations are verified locally, but the JetBrains plugin was not detected on this machine during the latest run.
- A Windows packaged-bridge crash caused by serializing a live `asyncio` subprocess handle has now been fixed and the ACP executables were rebuilt.
- FIX/CODE mutating actions are now confirmation-first by default in ACP; `brave_mode=on` or `/brave` bypasses confirmations without weakening workflow restrictions.
- HuggingFace ACP templates now use `Qwen/Qwen3-Coder-Next-FP8:together` on `https://router.huggingface.co/v1` and pass auth through `HF_TOKEN`, which the bridge maps to `OPENAI_API_KEY` for the runtime.
- OpenRouter ACP launches now also normalize `OPEN_ROUTER_KEY` into `OPENAI_API_KEY` for the spawned runtime.
- `dist\\openclaude-acp-low.exe` remained locked during the latest rebuild, so `dist\\openclaude-acp-low-updated.exe` is the current replacement artifact until the lock is released.
- `dist\\openclaude-acp-low-updated.exe` also became locked during the latest rebuild, so `dist\\openclaude-acp-low-v2.exe` is the newest LOW replacement artifact with the raw tool-call fallback fix.
- `dist\\openclaude-acp-high.exe` also remained locked during the latest rebuild, so `dist\\openclaude-acp-high-updated.exe` is the current replacement artifact until the lock is released.
- The ACP bridge now detects Windows vs Linux for launcher selection and tells the runtime to prefer PowerShell on Windows and Bash on Linux.
- Early-stop and launch-failure paths now return a final ACP assistant message with the reason instead of terminating the turn abruptly.
- XML-style raw tool-call text from OpenAI-compatible providers is now converted back into real tool calls before execution instead of leaking into the user-visible answer.
- Windows raw XML-style `Bash` tool-call fallback now remaps to `PowerShell` and preserves the original tool name in synthesized input for diagnostics.
- Runtime shell-tool lookup now also normalizes Windows `Bash` calls to `PowerShell`, and the Windows built-in tool list prefers `PowerShell` when that tool is enabled.
- The open-repo `src/utils/antModelOverrideConfig.ts` stub is required for clean builds; keep it checked in so imports of `./antModelOverrideConfig.js` resolve on fresh systems.
- `AI WORKFLOW/{AGENTS,PLAN,PROGRESS,NEXT_TASKS}.md` is now auto-loaded by the runtime instruction-memory pipeline when present.
- The `docs_en` runtime wiki has now been audited against the codebase in `docs_en/FEATURE_AUDIT.md`; use that audit when choosing the next provider-neutralization batch.

---

## Done Criteria For Current Batch
- [x] Verification matrix executed locally over ACP stdio and results documented.
- [ ] JetBrains ACP behavior confirmed in the real IDE for config options, four workflow modes, `brave_mode`, slash commands, and IDEA MCP tools.
- [x] LOW/HIGH dedicated executables validated from ACP JSON presets locally via ACP JSON template checks.
- [x] Workflow restrictions refined locally so FIX/CODE mutating actions are confirmation-first by default with an explicit brave bypass.
- [x] Session persistence validated across bridge restart scenarios via the ACP stdio harness; still needs one real IDE confirmation pass.
- [x] Platform-aware launch behavior and non-abrupt early-stop handling are implemented and regression-tested locally.
- [x] Raw XML-style shell tool-call fallback is now OS-aware locally, including Windows remapping from provider-emitted `Bash` markup to the `PowerShell` tool.
- [x] Runtime shell-tool lookup and Windows tool exposure now align with the same Bash-to-PowerShell remap behavior used by the raw XML fallback path.
- [ ] Provider templates validated in real environments with successful prompt execution after the rebuilt Windows bridge is retested.
- [ ] Shared-runtime provider-neutralization advanced enough that remaining open-provider paths no longer depend on Anthropic SDK message/type plumbing, except where JetBrains MCP replaces the need directly.

---

## After Completion
Update:
- `PROGRESS.md` with what was completed and any key decisions
- `NEXT_TASKS.md` with the next batch
- `PLAN.md` only if roadmap or scope changed
