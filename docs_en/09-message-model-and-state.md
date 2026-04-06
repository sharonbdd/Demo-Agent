# 09. Message Model And State

## Overview

The runtime uses explicit message and state models rather than raw strings.

## Message Types

The system works with multiple message classes, including:

- user
- assistant
- system
- attachment
- progress
- tool-related synthetic messages
- SDK stream/control messages

Important consequences:

- not every UI message belongs in the transcript
- not every transcript message should be sent back to the model
- some messages exist only to preserve tool correctness or remote protocol behavior

## App State

`src/state/AppStateStore.ts` stores the interactive session state, including:

- settings and selected model
- permission context
- task registry
- agent registry
- notifications
- MCP clients, commands, and resources
- plugin and bridge state
- prompt suggestion and thinking flags

This is the operator-facing state container.

## Bootstrap State

`src/bootstrap/state.ts` stores cross-cutting session and process state, such as:

- cwd and project root
- session id and parent session id
- telemetry counters
- last API request metadata
- cached prompt sections
- session-only flags
- additional directories and channel allowlists

This is the runtime-facing global state container.

## Session Message Semantics

`src/utils/sessionStorage.ts` carefully distinguishes:

- messages that are durable transcript truth
- progress updates that should not distort the parent chain
- task artifacts that live outside the main transcript

That distinction is essential for correct resume behavior.

## SDK State Exposure

The system can expose runtime state outward via SDK messages such as `system/init`, making tools, commands, plugins, agents, and MCP servers visible to remote consumers.

## Design Lessons

- Use separate state containers for UI state and global runtime state.
- Model message types explicitly to avoid replay and persistence bugs.
- Persist only the messages that represent actual conversation history.
