# Agent-ACP Verification Results

Last updated: 2026-04-06

## Local ACP Protocol And Binary Verification
- Rebuilt `dist/cli.mjs`, `dist/openclaude-acp-low.exe`, `dist/openclaude-acp-high.exe`, and `dist/openclaude-acp-modes.exe`.
- Verified the rebuilt binaries over ACP stdio using the Python ACP client.
- Executed session-control verification against the dedicated LOW and HIGH executables:
  - `initialize`
  - `new_session`
  - `session/set_mode`
  - `session/set_config_option`
  - slash-command prompt updates
  - `session/list`
  - `session/load`
  - `session/resume`
- Verified persisted ACP session state survives bridge restart using a real on-disk ACP state file.

## ACP JSON Template Verification
- Validated all checked-in ACP JSON templates launch over ACP successfully.
- Verified the provider/profile matrix is complete for:
  - OpenRouter LOW/HIGH
  - OpenAI LOW/HIGH
  - HuggingFace LOW/HIGH
  - Ollama LOW/HIGH
  - Local OpenAI LOW/HIGH
- Verified the primary templates point at the dedicated `openclaude-acp-low.exe` and `openclaude-acp-high.exe` launchers.
- Sanitized the legacy `old.json` compatibility sample and confirmed checked-in ACP JSON files no longer contain live-style secrets.

## Tool Verification
- Added a Bun-backed tool registry audit for the open build.
- Verified the default open-build tool surface is registered and stable.
- Verified env-gated open-repo tools register when enabled:
  - `PowerShell`
  - `TaskCreate`
  - `TaskGet`
  - `TaskUpdate`
  - `TaskList`
  - `LSP`
  - `TestingPermission`
- Verified the checked-in JetBrains ACP config template keeps `use_idea_mcp=true` and preserves the expected IDEA MCP allowlist.

## Runtime Smoke
- `bun run smoke` passed.
- `bun run doctor:runtime:json` passed.

## Real Environment Findings
- Live OpenRouter ACP prompt smoke was attempted with the local `OPEN_ROUTER_KEY` environment and currently fails with `RequestError: Internal error`.
- Live HuggingFace ACP prompt smoke was attempted using the local `~/.jetbrains/acp.json` ACP configuration and currently fails with `RequestError: Internal error`.
- A PyCharm process was running during verification, but the JetBrains Claude/OpenClaude plugin was not detected by the repo's JetBrains plugin discovery logic, so real IDEA MCP tool execution could not be confirmed from the local runtime alone.

## Still Blocked
- Root-cause the runtime/provider failure behind ACP prompt turns in real OpenRouter and HuggingFace environments.
- Install or confirm the JetBrains plugin so IDEA MCP tools can be exercised from a live IDE-backed ACP session.
- Execute a true end-to-end JetBrains UI verification pass once the above two blockers are resolved.
