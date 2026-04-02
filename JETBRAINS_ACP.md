# JetBrains ACP Setup

This repo does not expose ACP natively. The local setup here uses a thin ACP bridge that launches the existing OpenClaude headless CLI without changing agent logic.

## What this uses

- OpenClaude build output: `dist/cli.mjs`
- OpenRouter launcher: `bin/openclaude-openrouter.cmd`
- Local terminal executable: `dist/openclaude-local/openclaude-local.exe`
- ACP bridge source: `scripts/openclaude_acp_bridge.py`
- ACP bridge executable: `dist/openclaude-acp-modes.exe`

## Required environment

Set one of these before launching from JetBrains:

- `OPEN_ROUTER_KEY`
- `OPENROUTER_API_KEY`
- `OPENAI_API_KEY`

The launcher maps those into the repo's existing OpenAI-compatible shim and defaults to:

- `OPENAI_BASE_URL=https://openrouter.ai/api/v1`
- `OPENAI_MODEL=qwen/qwen3.6-plus:free`
- `CLAUDE_CODE_USE_OPENAI=1`

## Local launch

Use either of these for direct local agent use:

- `F:\PyCharm\openclaude\dist\openclaude-local\openclaude-local.exe`
- `F:\PyCharm\openclaude\bin\openclaude-openrouter.cmd`

Both preserve the repo's existing agent logic and only supply the OpenRouter/OpenAI-compatible runtime wiring.

## ACP modes

The ACP bridge exposes these session modes to JetBrains:

- `Ask`: no tools, no slash commands, pure model interaction
- `Plan`: read/search/fetch-only tool access
- `Agent`: normal agent mode with permission prompts
- `Agent (full access)`: full agent mode with permission prompts bypassed

## JetBrains acp.json

JetBrains ACP config is `~/.jetbrains/acp.json`. The format is:

```json
{
  "default_mcp_settings": {
    "use_custom_mcp": true,
    "use_idea_mcp": true
  },
  "agent_servers": {
    "OpenClaude OpenRouter": {
      "command": "F:\\PyCharm\\openclaude\\dist\\openclaude-acp-modes.exe",
      "env": {
        "OPENCLAUDE_REPO_ROOT": "F:\\PyCharm\\openclaude",
        "OPEN_ROUTER_KEY": "sk-or-v1-..."
      }
    }
  }
}
```

The config snippet shown in the chat was not an ACP config. It was an OpenCode provider config and JetBrains will not use it as a custom ACP agent.

## Notes

- For JetBrains workflow integration, keep `use_idea_mcp` as `true` so the IDE MCP server is exposed to the agent.
- Keep `use_custom_mcp` as `true` if you want JetBrains user-configured MCP servers exposed as well.
- The ACP bridge currently runs one OpenClaude headless process per prompt and resumes the same OpenClaude session ID across prompts.
- JetBrains uses ACP session methods that are still marked unstable in the Python ACP runtime. The bundled bridge enables that protocol so `session/set_model` works correctly.
- Bun is installed locally at `C:\Users\Sharon Boddu\AppData\Local\Microsoft\WinGet\Packages\Oven-sh.Bun_Microsoft.Winget.Source_8wekyb3d8bbwe\bun-windows-x64\bun.exe`, but it is not currently on `PATH`.
- `node` and `npm` are not currently on `PATH`. If you want them globally, install with `winget install OpenJS.NodeJS.LTS`.

## Troubleshooting

- `OpenAI API error 404: No endpoints available matching your guardrail restrictions and data policy`
  This comes from OpenRouter account privacy settings, not from JetBrains ACP. For free models, OpenRouter may block routing if your privacy settings only allow providers with stricter data policies than the model currently offers. Adjust `https://openrouter.ai/settings/privacy` for free-model routing, or choose providers/models that satisfy your account policy.
- `OpenAI API error 404: No endpoints found matching your data policy (Free model training)`
  This is the more specific OpenRouter failure for `:free` model variants when the privacy toggle for free-model training is disabled in your OpenRouter account.
- `Method not found` for `session/set_model`
  This means the ACP bridge was launched without unstable ACP session methods enabled. Use the rebuilt `dist/openclaude-acp-modes.exe`.
- `No session managers found for agent 'OpenClaude OpenRouter'`
  JetBrains logs this when the ACP process fails during initialization or early session setup. Fix the ACP executable path first, then retry after restarting the IDE.
