# 05. Commands, UI, And Operator Experience

## Overview

The operator interface is not just a text prompt. The repository includes a full command system, interactive TUI components, dialogs, status indicators, and SDK/structured output paths.

Key modules:

- `src/main.tsx`
- `src/commands.ts`
- `src/interactiveHelpers.tsx`
- `src/ink.ts`
- `src/state/AppStateStore.ts`

## Slash Command System

`src/commands.ts` aggregates a large command surface including:

- session controls
- config and permissions
- memory and context inspection
- review, diff, doctor, compact
- plugin and MCP management
- bridge and remote flows
- tasks, agents, plan mode, model selection

Commands come from multiple sources:

- built-in commands
- skill-provided commands
- plugin commands

## TUI State

The main interactive UI keeps substantial runtime state in `AppStateStore`, including:

- task panels
- footer selection
- MCP connection state
- plugin state
- notifications
- bridge status
- remote viewer state
- prompt suggestion and thinking flags

This lets the CLI act like an operating console for the agent, not just a REPL.

## Operator Feedback

The UI surfaces:

- tool progress
- background task activity
- permission prompts
- task notifications
- bridge connectivity
- mode switches
- plugin installation status

## Headless And SDK Paths

The product is also designed to work without the full TUI:

- `QueryEngine` emits SDK messages
- `system/init` messages announce tools, commands, plugins, and agents
- structured I/O and control messages support remote clients

## Design Lessons

- Agent UX improves when state is visible.
- Commands should be first-class runtime entrypoints, not prompt hacks.
- The same core engine should support both rich TUI and headless automation.
