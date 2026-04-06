# 02. Tools, Permissions, And Execution

## Overview

The tool pipeline is one of the strongest parts of this codebase. Tools are typed, discoverable, permission-aware, and integrated into the conversation loop.

Key modules:

- `src/Tool.ts`
- `src/tools.ts`
- `src/services/tools/toolOrchestration.ts`
- `src/services/tools/StreamingToolExecutor.ts`
- `src/utils/permissions/*`
- `src/utils/hooks/*`

## Tool Families

The base tool registry includes capabilities such as:

- file read, write, edit, notebook edit
- grep and glob
- bash and optional PowerShell
- web fetch and web search
- todo/task tools
- agent spawning and messaging
- skill invocation
- MCP tool and resource access
- user interaction tools such as plan-mode exit and questions

Many tools are feature-gated and only load when the build or environment enables them.

## Tool Definition Model

Each tool participates in a common contract:

- name
- input schema
- enablement check
- validation
- concurrency behavior
- interrupt behavior
- execution function

This is why the runtime can treat tool execution as a pipeline rather than ad hoc logic.

## Execution Pipeline

For each tool call, the runtime generally does the following:

1. resolve the tool by name
2. parse and validate input
3. run tool-specific validation
4. consult hooks and permission logic
5. execute the tool
6. stream progress messages if supported
7. normalize the result into conversation messages
8. update runtime context if needed

`src/services/tools/toolOrchestration.ts` batches read-only or concurrency-safe tools together. `src/services/tools/StreamingToolExecutor.ts` lets streaming trajectories start tools as they arrive while still preserving ordered result emission.

## Permissions Model

The permission system is layered rather than binary.

Inputs include:

- current permission mode
- allow/deny/ask rules from settings and session state
- auto-mode restrictions
- dangerous-pattern filters
- hook results
- working-directory restrictions
- sandbox overrides

Important modules:

- `src/utils/permissions/permissions.ts`
- `src/utils/permissions/permissionSetup.ts`
- `src/utils/permissions/permissionsLoader.ts`

## Why Shell Tools Are Special

The repo explicitly treats command execution as higher risk than structured tools:

- dangerous prefix patterns are filtered
- Bash and PowerShell have dedicated danger checks
- auto-mode strips unsafe rules
- shell commands may require sandbox escalation or manual approval

The design principle is simple: a generic shell is the escape hatch for everything else, so it needs the strongest governance.

## Hooks

Hooks are used to insert runtime policy and automation around execution. They can:

- block
- request approval
- add context
- trigger side effects
- inspect session lifecycle events

The hook system is part of the execution architecture, not a plugin afterthought.

## Result Handling

Tool execution does not just return raw stdout. Results are translated into structured conversation messages, progress events, and sometimes persisted outputs. This is what lets the query loop continue coherently after a tool finishes.

## Design Lessons

- Prefer dedicated tools over forcing everything through a shell.
- Make permission sources explicit and composable.
- Support progress and partial output for long-running tools.
- Model concurrency as a property of the tool, not as a global switch.
