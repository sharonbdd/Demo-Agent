# OpenClaude

Use Agent with **any LLM**.

OpenDemo is a fork of one of the SOTA agent. We added an OpenAI-compatible provider shim so you can plug in GPT-4o, DeepSeek, Gemini, Llama, Mistral, or any model that speaks the OpenAI chat completions API.

All of AI Agents's tools work — bash, file read/write/edit, grep, glob, agents, tasks, MCP — just powered by whatever model you choose.

---

## PyCharm Integration (Zero to 100)

OpenClaude can run in PyCharm as a custom ACP agent through the JetBrains AI plugin.

### 1. Prerequisites
- PyCharm with JetBrains AI Assistant enabled.
- Bun installed locally for the OpenClaude CLI runtime.
- Python 3.10+ for `scripts/openclaude_acp_bridge.py`.
- One provider configured: OpenRouter, OpenAI, HuggingFace, Ollama, or another OpenAI-compatible local server.

### 2. Build the runtime once
```powershell
bun run build
pip install pyinstaller agent-client-protocol
python -m PyInstaller --onefile scripts/openclaude_acp_low.py --distpath dist --name openclaude-acp-low
python -m PyInstaller --onefile scripts/openclaude_acp_high.py --distpath dist --name openclaude-acp-high
```

This produces:
- `dist/cli.mjs`
- `dist/openclaude-acp-low.exe` and `dist/openclaude-acp-high.exe` on Windows
- `dist/openclaude-acp-low` and `dist/openclaude-acp-high` on Linux when built there

### 3. Configure `~/.jetbrains/acp.json`
```json
{
  "default_mcp_settings": {
    "use_custom_mcp": true,
    "use_idea_mcp": true
  },
  "agent_servers": {
    "OpenClaude LOW": {
      "command": "F:\\PyCharm\\Demo-Agent\\dist\\openclaude-acp-low.exe",
      "env": {
        "OPENCLAUDE_REPO_ROOT": "F:\\PyCharm\\Demo-Agent",
        "OPEN_ROUTER_KEY": "your-api-key-here",
        "OPENAI_BASE_URL": "https://openrouter.ai/api/v1",
        "OPENAI_MODEL": "qwen/qwen3.6-plus:free",
        "OPENCLAUDE_MODEL_PROVIDER": "openrouter",
        "OPENCLAUDE_ACP_DEFAULT_CONTEXT_PROFILE": "low",
        "OPENCLAUDE_ACP_DEFAULT_WORKFLOW_MODE": "code",
        "CLAUDE_CODE_USE_OPENAI": "1"
      }
    },
    "OpenClaude HIGH": {
      "command": "F:\\PyCharm\\Demo-Agent\\dist\\openclaude-acp-high.exe",
      "env": {
        "OPENCLAUDE_REPO_ROOT": "F:\\PyCharm\\Demo-Agent",
        "OPEN_ROUTER_KEY": "your-api-key-here",
        "OPENAI_BASE_URL": "https://openrouter.ai/api/v1",
        "OPENAI_MODEL": "openai/gpt-4o",
        "OPENCLAUDE_MODEL_PROVIDER": "openrouter",
        "OPENCLAUDE_ACP_DEFAULT_CONTEXT_PROFILE": "high",
        "OPENCLAUDE_ACP_DEFAULT_WORKFLOW_MODE": "code",
        "CLAUDE_CODE_USE_OPENAI": "1"
      }
    }
  }
}
```

Provider examples:
- OpenRouter: `OPENAI_BASE_URL=https://openrouter.ai/api/v1`
- HuggingFace: `OPENAI_BASE_URL=https://router.huggingface.co/v1`
- Ollama: `OPENAI_BASE_URL=http://localhost:11434/v1`
- Local OpenAI-compatible server: `OPENAI_BASE_URL=http://localhost:8080/v1`

Optional bridge env:
- `OPENCLAUDE_ACP_MODELS=model-a,model-b` to fully override the model picker
- `OPENCLAUDE_EXTRA_MODELS=model-c,model-d` to append choices
- `OPENCLAUDE_MODEL_PROVIDER=openrouter|huggingface|openai|ollama|local_openai|auto`
- `OPENCLAUDE_ACP_DEFAULT_CONTEXT_PROFILE=low|high` to pin the default profile for a launcher
- `OPENCLAUDE_ACP_DEFAULT_WORKFLOW_MODE=ask|plan|fix|code` to pin the default workflow role

For OpenRouter presets, `OPEN_ROUTER_KEY`, `OPENROUTER_API_KEY`, and `OPENAI_API_KEY` are all accepted. The bundled Windows launcher maps the OpenRouter-specific names into `OPENAI_API_KEY` automatically.

### 4. ACP session modes
- **Ask**: consultant/spec mode, no edits, read-only tools
- **Plan**: architect mode, Markdown-only edits plus read/search/fetch tools
- **Fix**: tester/debugger mode, bounded repair workflow
- **Code**: normal implementation mode

Capacity profile is a separate control from workflow mode:
- **LOW**: smaller context budget, earlier compaction, concise planning
- **HIGH**: larger context budget, richer replay, deeper planning and verification

You can switch profiles and workflow roles in-session via ACP config options or slash commands such as `/low`, `/high`, `/ask`, `/plan`, `/fix`, and `/code`.

---

## Tool Capability Inventory

The source of truth is `src/tools.ts`. In the open build, tool availability falls into three buckets:

- `Available`: present in the default open build when the normal runtime conditions are met.
- `Conditional`: built from source but requires an env flag, runtime mode, or optional feature gate.
- `Disabled in open build`: referenced in source, but the current `scripts/build.ts` turns the feature flag off.

### Available now

| Tool | Status | Notes |
|------|--------|-------|
| `Agent` | Available | Sub-agent execution entry point. Legacy alias: `Task`. |
| `AskUserQuestion` | Available | Interactive clarification prompt. |
| `Bash` | Available | Shell execution on Unix-like environments. |
| `Edit` | Available | Surgical file edits. |
| `Read` | Available | File reads with range and size controls. |
| `Write` | Available | Full file writes. |
| `Glob` | Available | File pattern search when embedded search tools are absent. |
| `Grep` | Available | Text search when embedded search tools are absent. |
| `NotebookEdit` | Available | Notebook-specific editing. |
| `WebFetch` | Available | URL fetch and markdown conversion. |
| `WebSearch` | Available | Web search integration. |
| `TodoWrite` | Available | Session todo state updates. |
| `TaskStop` | Available | Stop current multi-step task. |
| `SendUserMessage` | Available | User-facing summary/message tool. Legacy alias: `Brief`. |
| `Skill` | Available | Executes installed skill workflows. |
| `EnterPlanMode` | Available | Switches agent into planning state. |
| `ListMcpResourcesTool` | Available | Lists MCP resources. |
| `ReadMcpResource` | Available | Reads MCP resources. |
| `SendMessage` | Available | Message another agent or teammate. |
| `ToolSearch` | Conditional | Available when tool-search gating is enabled. |
| `PowerShell` | Conditional | Available when shell detection enables Windows PowerShell support. |

### Conditional in the open repo

| Tool | Status | Enablement |
|------|--------|------------|
| `TaskCreate` | Conditional | Requires Todo v2/task support. |
| `TaskGet` | Conditional | Requires Todo v2/task support. |
| `TaskUpdate` | Conditional | Requires Todo v2/task support. |
| `TaskList` | Conditional | Requires Todo v2/task support. |
| `LSP` | Conditional | Requires `ENABLE_LSP_TOOL`. |
| `EnterWorktree` | Conditional | Requires worktree mode. |
| `ExitWorktree` | Conditional | Requires worktree mode. |
| `REPL` | Conditional | Ant-only runtime path. |
| `Config` | Conditional | Ant-only runtime path. |
| `Tungsten` | Conditional | Ant-only runtime path. |
| `TestingPermission` | Conditional | Test-only (`NODE_ENV=test`). |
| `VerifyPlanExecution` | Conditional | Requires `CLAUDE_CODE_VERIFY_PLAN=true`. |

### Present in source, disabled by the current open build flags

| Tool | Status | Source gating |
|------|--------|---------------|
| `SuggestBackgroundPR` | Disabled in open build | `PROACTIVE` |
| `Sleep` | Disabled in open build | `PROACTIVE` or `KAIROS` |
| `CronCreate` | Disabled in open build | `AGENT_TRIGGERS` |
| `CronDelete` | Disabled in open build | `AGENT_TRIGGERS` |
| `CronList` | Disabled in open build | `AGENT_TRIGGERS` |
| `RemoteTrigger` | Disabled in open build | `AGENT_TRIGGERS_REMOTE` |
| `Monitor` | Disabled in open build | `MONITOR_TOOL` |
| `SendUserFile` | Disabled in open build | `KAIROS` |
| `PushNotification` | Disabled in open build | `KAIROS` or `KAIROS_PUSH_NOTIFICATION` |
| `SubscribePR` | Disabled in open build | `KAIROS_GITHUB_WEBHOOKS` |
| `OverflowTest` | Disabled in open build | `OVERFLOW_TEST_TOOL` |
| `CtxInspect` | Disabled in open build | `CONTEXT_COLLAPSE` |
| `TerminalCapture` | Disabled in open build | `TERMINAL_PANEL` |
| `WebBrowser` | Disabled in open build | `WEB_BROWSER_TOOL` |
| `Snip` | Disabled in open build | `HISTORY_SNIP` |
| `ListPeers` | Disabled in open build | `UDS_INBOX` |
| `WorkflowTool` | Disabled in open build | `WORKFLOW_SCRIPTS` |
| `TeamCreate` | Disabled in open build | agent swarms/team mode |
| `TeamDelete` | Disabled in open build | agent swarms/team mode |

### Internal or protocol-level capabilities

These exist as tool-adjacent capabilities but are not normal end-user built-ins in the current open build:

- `StructuredOutput`
- MCP server tools created dynamically from connected MCP servers
- `McpAuthTool`
- `MCPTool` wrapper infrastructure

Across base tools, aliases, conditional tools, disabled-by-flag tools, and protocol-generated MCP tools, the repo exposes well over 47 tool-calling capabilities.

---

## Quick Start

### 1. Set 3 environment variables

```bash
export CLAUDE_CODE_USE_OPENAI=1
export OPENAI_API_KEY=sk-your-key-here
export OPENAI_MODEL=gpt-4o
```

### 2. Run it

```bash
# If installed via npm
openclaude

# If built from source
bun run dev
# or after build:
node dist/cli.mjs
```

That's it. The tool system, streaming, file editing, multi-step reasoning — everything works through the model you picked.

The npm package name is `@gitlawb/openclaude`, but the installed CLI command is still `openclaude`.

---

## Provider Examples

### OpenAI

```bash
export CLAUDE_CODE_USE_OPENAI=1
export OPENAI_API_KEY=sk-...
export OPENAI_MODEL=gpt-4o
```

### DeepSeek

```bash
export CLAUDE_CODE_USE_OPENAI=1
export OPENAI_API_KEY=sk-...
export OPENAI_BASE_URL=https://api.deepseek.com/v1
export OPENAI_MODEL=deepseek-chat
```

### Google Gemini (via OpenRouter)

```bash
export CLAUDE_CODE_USE_OPENAI=1
export OPENAI_API_KEY=sk-or-...
export OPENAI_BASE_URL=https://openrouter.ai/api/v1
export OPENAI_MODEL=google/gemini-2.0-flash
```

If OpenRouter returns `No endpoints available matching your guardrail restrictions and data policy`, review your account privacy settings at `https://openrouter.ai/settings/privacy`. Free models often require less restrictive routing settings than paid provider tiers.

### Ollama (local, free)

```bash
ollama pull llama3.3:70b

export CLAUDE_CODE_USE_OPENAI=1
export OPENAI_BASE_URL=http://localhost:11434/v1
export OPENAI_MODEL=llama3.3:70b
# no API key needed for local models
```

### LM Studio (local)

```bash
export CLAUDE_CODE_USE_OPENAI=1
export OPENAI_BASE_URL=http://localhost:1234/v1
export OPENAI_MODEL=your-model-name
```

### Together AI

```bash
export CLAUDE_CODE_USE_OPENAI=1
export OPENAI_API_KEY=...
export OPENAI_BASE_URL=https://api.together.xyz/v1
export OPENAI_MODEL=meta-llama/Llama-3.3-70B-Instruct-Turbo
```

### Groq

```bash
export CLAUDE_CODE_USE_OPENAI=1
export OPENAI_API_KEY=gsk_...
export OPENAI_BASE_URL=https://api.groq.com/openai/v1
export OPENAI_MODEL=llama-3.3-70b-versatile
```

### Mistral

```bash
export CLAUDE_CODE_USE_OPENAI=1
export OPENAI_API_KEY=...
export OPENAI_BASE_URL=https://api.mistral.ai/v1
export OPENAI_MODEL=mistral-large-latest
```

### Azure OpenAI

```bash
export CLAUDE_CODE_USE_OPENAI=1
export OPENAI_API_KEY=your-azure-key
export OPENAI_BASE_URL=https://your-resource.openai.azure.com/openai/deployments/your-deployment/v1
export OPENAI_MODEL=gpt-4o
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `CLAUDE_CODE_USE_OPENAI` | Yes | Set to `1` to enable the OpenAI provider |
| `OPENAI_API_KEY` | Yes* | Your API key (*not needed for local models like Ollama) |
| `OPENAI_MODEL` | Yes | Model name (e.g. `gpt-4o`, `deepseek-chat`, `llama3.3:70b`) |
| `OPENAI_BASE_URL` | No | API endpoint (defaults to `https://api.openai.com/v1`) |
| `OPENAI_REQUEST_DELAY_MS` | No | Minimum delay in milliseconds between LLM requests. Default: `500` (to prevent rapid-fire rate limits). |

You can also use `ANTHROPIC_MODEL` to override the model name. `OPENAI_MODEL` takes priority.

---

## Runtime Hardening

Use these commands to keep the CLI stable and catch environment mistakes early:

```bash
# quick startup sanity check
bun run smoke

# validate provider env + reachability
bun run doctor:runtime

# print machine-readable runtime diagnostics
bun run doctor:runtime:json

# persist a diagnostics report to reports/doctor-runtime.json
bun run doctor:report

# full local hardening check (typecheck + smoke + runtime doctor)
bun run hardening:check

# strict hardening (includes project-wide typecheck)
bun run hardening:strict
```

Notes:
- `doctor:runtime` fails fast if `CLAUDE_CODE_USE_OPENAI=1` with a placeholder key (`SUA_CHAVE`) or a missing key for non-local providers.
- Local providers (for example `http://localhost:11434/v1`) can run without `OPENAI_API_KEY`.

### Provider Launch Profiles

Use profile launchers to avoid repeated environment setup:

```bash
# one-time profile bootstrap (auto-detect ollama, otherwise openai)
bun run profile:init

# openai bootstrap with explicit key
bun run profile:init -- --provider openai --api-key sk-...

# ollama bootstrap with custom model
bun run profile:init -- --provider ollama --model llama3.1:8b

# launch using persisted profile (.openclaude-profile.json)
bun run dev:profile

# OpenAI profile (requires OPENAI_API_KEY in your shell)
bun run dev:openai

# Ollama profile (defaults: localhost:11434, llama3.1:8b)
bun run dev:ollama
```

`dev:openai` and `dev:ollama` run `doctor:runtime` first and only launch the app if checks pass.
For `dev:ollama`, make sure Ollama is running locally before launch.

---

## Build Instructions

### Cross-Platform Executables (v2.0)

#### CLI Executable
To bundle the OpenClaude CLI into a standalone binary:

**Windows:**
```bash
bun build --compile --target=bun-windows-x64 ./src/entrypoints/cli.tsx --outfile dist/openclaude-local/openclaude-local.exe
```

**Linux:**
```bash
bun build --compile --target=bun-linux-x64 ./src/entrypoints/cli.tsx --outfile dist/openclaude-linux
```

Or use the helper script:
```bash
./scripts/build-linux.sh
```

#### ACP Bridge
The ACP bridge is a Python script that requires the `agent-client-protocol` library.

To create standalone binaries:
```bash
pip install pyinstaller agent-client-protocol
python -m PyInstaller --onefile scripts/openclaude_acp_low.py --distpath dist --name openclaude-acp-low
python -m PyInstaller --onefile scripts/openclaude_acp_high.py --distpath dist --name openclaude-acp-high
```
*(On Linux, this will produce ELF binaries named `openclaude-acp-low` and `openclaude-acp-high` in `dist/`)*

Optional compatibility build:
```bash
python -m PyInstaller --onefile scripts/openclaude_acp_bridge.py --distpath dist --name openclaude-acp-modes
```

Recommended Linux packaging flow:
```bash
bun run build
bun build --compile --target=bun-linux-x64 ./src/entrypoints/cli.tsx --outfile dist/openclaude-linux/openclaude
python3 -m PyInstaller --onefile scripts/openclaude_acp_low.py --distpath dist/openclaude-linux --name openclaude-acp-low
python3 -m PyInstaller --onefile scripts/openclaude_acp_high.py --distpath dist/openclaude-linux --name openclaude-acp-high
```

---

## Provider Configuration (v2.0)

### HuggingFace API
To use HuggingFace Inference Endpoints:
```bash
export CLAUDE_CODE_USE_OPENAI=1
export OPENAI_BASE_URL=https://router.huggingface.co/v1
export OPENAI_API_KEY=hf_your_token_here
export OPENAI_MODEL=meta-llama/Llama-3.3-70B-Instruct
```

### Local OpenAI (LM Studio / LocalAI)
To use a generic OpenAI-compatible local server:
```bash
export CLAUDE_CODE_USE_OPENAI=1
export OPENAI_BASE_URL=http://localhost:8080/v1
export OPENAI_API_KEY=any-value-or-empty
export OPENAI_MODEL=your-local-model
```

---

- **All tools**: Bash, FileRead, FileWrite, FileEdit, Glob, Grep, WebFetch, WebSearch, Agent, MCP, LSP, NotebookEdit, Tasks
- **Streaming**: Real-time token streaming
- **Tool calling**: Multi-step tool chains (the model calls tools, gets results, continues)
- **Images**: Base64 and URL images passed to vision models
- **Slash commands**: /commit, /review, /compact, /diff, /doctor, etc.
- **Sub-agents**: AgentTool spawns sub-agents using the same provider
- **Memory**: Persistent memory system

## What's Different

- **No thinking mode**: Anthropic's extended thinking is disabled (OpenAI models use different reasoning)
- **No prompt caching**: Anthropic-specific cache headers are skipped
- **No beta features**: Anthropic-specific beta headers are ignored
- **Token limits**: Defaults to 32K max output — some models may cap lower, which is handled gracefully

---

## How It Works

The shim (`src/services/api/openaiShim.ts`) sits between Claude Code and the LLM API:

```
Claude Code Tool System
        |
        v
  Anthropic SDK interface (duck-typed)
        |
        v
  openaiShim.ts  <-- translates formats
        |
        v
  OpenAI Chat Completions API
        |
        v
  Any compatible model
```

It translates:
- Anthropic message blocks → OpenAI messages
- Anthropic tool_use/tool_result → OpenAI function calls
- OpenAI SSE streaming → Anthropic stream events
- Anthropic system prompt arrays → OpenAI system messages

The rest of Claude Code doesn't know it's talking to a different model.

---

## Model Quality Notes

Not all models are equal at agentic tool use. Here's a rough guide:

| Model | Tool Calling | Code Quality | Speed |
|-------|-------------|-------------|-------|
| GPT-4o | Excellent | Excellent | Fast |
| DeepSeek-V3 | Great | Great | Fast |
| Gemini 2.0 Flash | Great | Good | Very Fast |
| Llama 3.3 70B | Good | Good | Medium |
| Mistral Large | Good | Good | Fast |
| GPT-4o-mini | Good | Good | Very Fast |
| Qwen 2.5 72B | Good | Good | Medium |
| Smaller models (<7B) | Limited | Limited | Very Fast |

For best results, use models with strong function/tool calling support.

---

## Files Changed from Original

```
src/services/api/openaiShim.ts   — NEW: OpenAI-compatible API shim (724 lines)
src/services/api/client.ts       — Routes to shim when CLAUDE_CODE_USE_OPENAI=1
src/utils/model/providers.ts     — Added 'openai' provider type
src/utils/model/configs.ts       — Added openai model mappings
src/utils/model/model.ts         — Respects OPENAI_MODEL for defaults
src/utils/auth.ts                — Recognizes OpenAI as valid 3P provider
```

6 files changed. 786 lines added. Zero dependencies added.

---

## Origin

This is a fork of [instructkr/claude-code](https://gitlawb.com/node/repos/z6MkgKkb/instructkr-claude-code), which mirrored the Claude Code source snapshot that became publicly accessible through an npm source map exposure on March 31, 2026.

The original Claude Code source is the property of Anthropic. This repository is not affiliated with or endorsed by Anthropic.

---

## License

This repository is provided for educational and research purposes. The original source code is subject to Anthropic's terms. The OpenAI shim additions are public domain.
