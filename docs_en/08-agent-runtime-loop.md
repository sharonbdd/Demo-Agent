# 08. Agent Runtime Loop

## Overview

The main loop is spread across `src/main.tsx`, `src/QueryEngine.ts`, and `src/query.ts`.

`main.tsx` handles startup and mode selection. `QueryEngine` owns conversation state across turns. `query.ts` runs the per-turn model/tool loop.

## Startup Phase

Before the first user turn, the runtime may:

- preload managed settings
- prefetch secure storage and auth data
- initialize telemetry
- load plugins and skills
- load MCP configs
- compute model and permission defaults
- recover or create session state

## Per-Turn Loop

At a high level, each turn does this:

1. accept user input or SDK prompt
2. gather system and user context
3. build the model request
4. stream assistant output
5. if tool calls appear, execute them
6. append tool results as messages
7. continue the loop until a terminal assistant response or stop condition

## Stop Conditions

A turn can stop because:

- the assistant produced a terminal text response
- max turns or token budgets were reached
- the user interrupted
- a fatal API or transport failure occurred
- a compaction/retry path ended without recovery

## Recovery Paths

`src/query.ts` contains explicit logic for non-happy-path execution, including:

- prompt-too-long handling
- reactive or automatic compaction
- max-output-token recovery
- stop-hook processing
- synthetic error/result message generation when needed

## Tool Execution Inside The Loop

Tool execution is not outside the loop. It is part of the same assistant trajectory:

- assistant emits `tool_use`
- runtime executes tool(s)
- runtime emits `tool_result` user messages
- model continues from that updated state

This is why the agent can perform multi-step work without the caller manually coordinating each substep.

## QueryEngine Responsibility

`QueryEngine` is especially important for headless or SDK usage because it:

- preserves messages across turns
- tracks usage and permission denials
- emits SDK-compatible events
- bridges transcript persistence and query execution

## Design Lessons

- Separate session lifetime from turn lifetime.
- Treat tool execution as part of the conversation state machine.
- Encode failure and recovery paths directly into the loop.
