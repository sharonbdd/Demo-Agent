# Future Plan

This repository cannot safely remove the Anthropic SDK end-to-end without changing shared runtime and protocol code outside the individual tool implementations.

## Tool-level changes completed now

- `WebFetchTool` no longer depends on Anthropic's hosted domain preflight endpoint.

## Tools deferred

The following tools remain unchanged because removing Anthropic SDK usage from them would require shared protocol/runtime changes, not isolated tool edits:

- `AgentTool`
- `AskUserQuestionTool`
- `BashTool`
- `BriefTool`
- `ConfigTool`
- `EnterPlanModeTool`
- `EnterWorktreeTool`
- `ExitPlanModeV2Tool`
- `ExitWorktreeTool`
- `FileEditTool`
- `FileReadTool`
- `FileWriteTool`
- `GlobTool`
- `GrepTool`
- `ListMcpResourcesTool`
- `LSPTool`
- `McpAuthTool`
- `MCPTool`
- `NotebookEditTool`
- `PowerShellTool`
- `ReadMcpResourceTool`
- `RemoteTriggerTool`
- `REPLTool`
- `CronCreateTool`
- `CronDeleteTool`
- `CronListTool`
- `SendMessageTool`
- `SkillTool`
- `SleepTool`
- `SuggestBackgroundPRTool`
- `SyntheticOutputTool`
- `TaskCreateTool`
- `TaskGetTool`
- `TaskListTool`
- `TaskOutputTool`
- `TaskStopTool`
- `TaskUpdateTool`
- `TeamCreateTool`
- `TeamDeleteTool`
- `TestingPermissionTool`
- `TodoWriteTool`
- `ToolSearchTool`
- `TungstenTool`
- `VerifyPlanExecutionTool`
- `WebSearchTool`
- `WorkflowTool`

## Why they are deferred

These tools still depend on one or more of the following shared Anthropic-shaped interfaces or services:

- `src/Tool.ts` imports Anthropic tool block types used by nearly every tool.
- `src/services/api/claude.ts` and `src/services/api/client.ts` own the message/query pipeline.
- `src/services/api/openaiShim.ts` emulates Anthropic message semantics for OpenAI-compatible providers instead of replacing them.
- `src/utils/errors.ts` depends on `APIUserAbortError` from the Anthropic SDK.
- Multiple UI and message types in `src/types/*`, `src/components/*`, and `src/services/tools/*` depend on Anthropic content block types.

## Specific blockers

### `WebSearchTool`

`WebSearchTool` is not safely convertible at the tool layer alone:

- It imports Anthropic beta web-search block types.
- It expects Anthropic-style `server_tool_use` and `web_search_tool_result` streaming events.
- The current OpenAI shim translates standard tool calls, but does not provide a provider-agnostic replacement for Anthropic's hosted web-search feature.

Future work:

1. Define provider-neutral web-search event/types in local code.
2. Add an OpenAI-compatible implementation path for search results and streaming progress.
3. Update the shim and query pipeline to emit provider-neutral search events.

### `FileReadTool`, `BashTool`, `ToolSearchTool`, and UI-heavy tools

These can lose direct SDK imports only after local protocol types are introduced and adopted across shared code:

1. Create local tool/content block types to replace imports from `@anthropic-ai/sdk/resources/*`.
2. Update `src/Tool.ts` and shared render/message plumbing to use those local types.
3. Replace the SDK abort error dependency in `src/utils/errors.ts`.
4. Re-run full typecheck and transcript/render tests.

## Recommended migration order

1. Introduce local protocol/type definitions.
2. Switch `src/Tool.ts`, `src/types/*`, and `src/components/messages/*` to those local types.
3. Replace shared error and message helpers that currently depend on Anthropic SDK classes/types.
4. Only then remove Anthropic SDK imports from the deferred tools.
5. Remove `@anthropic-ai/sdk` from dependencies after the shared runtime no longer imports it.
