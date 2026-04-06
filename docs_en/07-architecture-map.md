# 07. Architecture Map

## Top-Level Map

### Entry And Bootstrap

- `src/main.tsx`
- `src/bootstrap/state.ts`
- `src/interactiveHelpers.tsx`

Responsibilities:

- parse CLI options
- initialize global/session state
- load settings, plugins, skills, and MCP metadata
- choose interactive, SDK, or remote paths

### Prompt And Query Orchestration

- `src/context.ts`
- `src/query.ts`
- `src/QueryEngine.ts`
- `src/utils/queryContext.ts`

Responsibilities:

- assemble prompt context
- manage turn loop
- stream model output
- recover from token/compaction issues
- continue tool-driven trajectories

### Tool Layer

- `src/Tool.ts`
- `src/tools.ts`
- `src/services/tools/*`
- `src/tools/*`

Responsibilities:

- define tools
- validate input
- execute tools
- stream progress
- update runtime context

### Permissions And Hooks

- `src/utils/permissions/*`
- `src/utils/hooks/*`

Responsibilities:

- resolve allow/deny/ask decisions
- detect dangerous commands
- apply policy and session rules
- intercept lifecycle events

### Memory And Instructions

- `src/utils/claudemd.ts`
- `src/memdir/*`
- `src/commands/memory/*`

Responsibilities:

- discover repo and user instruction files
- manage typed durable memory
- support recall and editing workflows

### Session And Persistence

- `src/utils/sessionStorage.ts`
- `src/history.ts`
- `src/projectOnboardingState.ts`

Responsibilities:

- persist transcripts
- search and resume sessions
- store subagent and task artifacts

### Commands And UI

- `src/commands.ts`
- `src/commands/*`
- `src/state/AppStateStore.ts`

Responsibilities:

- expose slash commands
- render runtime state
- manage operator flows and dialogs

### Extensions

- `src/skills/*`
- `src/utils/plugins/*`
- `src/services/mcp/*`

Responsibilities:

- load bundled/local skills
- load plugin-packaged behaviors
- connect external MCP capabilities

### Tasks And Subagents

- `src/Task.ts`
- `src/tasks.ts`
- `src/tasks/*`
- `src/utils/task/*`

Responsibilities:

- spawn and track background work
- persist task outputs
- handle local, remote, and teammate execution

### Bridge And Remote Control

- `src/bridge/*`
- `src/cli/transports/*`
- `src/server/*`

Responsibilities:

- connect local sessions to remote control surfaces
- persist session-ingress traffic
- handle reconnect, heartbeat, token refresh, and remote transport state

### Configuration And Settings

- `src/utils/settings/*`
- `src/utils/config.ts`
- `src/services/remoteManagedSettings/*`

Responsibilities:

- merge settings sources
- validate schemas
- expose managed and policy-controlled runtime configuration

## Architectural Character

The codebase is best understood as a runtime OS for agents:

- bootstrap and identity
- prompt construction
- execution and governance
- persistence
- extension loading
- remote transport

The model call is central, but not dominant.
