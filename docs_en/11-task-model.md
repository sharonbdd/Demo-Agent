# 11. Task Model

## Overview

Tasks are first-class runtime objects. They are not just notes in the transcript.

Key modules:

- `src/Task.ts`
- `src/tasks.ts`
- `src/tasks/*`
- `src/utils/task/framework.ts`

## Task Types

The base task model currently includes types such as:

- `local_bash`
- `local_agent`
- `remote_agent`
- `in_process_teammate`
- `local_workflow`
- `monitor_mcp`
- `dream`

Feature flags determine which task kinds are available in a given build.

## Task State

Every task has shared state such as:

- id
- type
- status
- description
- output file
- start/end times
- notification state

Task status is explicit:

- pending
- running
- completed
- failed
- killed

## Why Tasks Matter

Tasks let the runtime represent work that outlives one immediate assistant reply:

- background shell execution
- delegated agent work
- remote job execution
- teammate/subagent work

## Output And Polling

Task output is persisted to disk and polled through the shared task framework. This is how the UI can show progress, notifications, and final states without forcing every result directly into the main transcript.

## Task Lifecycle

The framework supports:

- registration
- status updates
- polling
- attachment generation
- notification
- eager eviction after terminal states

## Design Lessons

- Background work should have its own model, not masquerade as chat.
- Persist task output separately from core conversation history.
- Keep task lifecycle transitions explicit and inspectable.
