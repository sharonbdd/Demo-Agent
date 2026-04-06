# 16. Python Implementation Notes

## Current Reality

The production runtime in this repository is TypeScript running on Bun/Node. The Python files in the repo are supporting experiments, tests, and provider-related utilities, not the main agent runtime.

## If Porting This Architecture To Python

Mirror the boundaries, not the language details.

## Recommended Python Module Split

### Bootstrap

- CLI parsing
- global/session state
- config loading

### Query engine

- conversation state per session
- per-turn execution loop
- streaming model integration

### Tool framework

- base tool interface
- JSON-schema or Pydantic validation
- tool registry
- concurrency policy

### Permissions and hooks

- rule loaders
- policy evaluation
- pre/post execution hook dispatch

### Persistence

- transcripts
- session metadata
- task output files
- memory directories

### Extensions

- skill loading
- plugin manifests
- MCP client integrations

## Architectural Rules To Preserve

- keep UI state separate from global runtime state
- distinguish transcript messages from ephemeral progress
- keep tool orchestration separate from model transport
- treat context assembly as its own subsystem
- make permissions part of normal execution, not an exception path

## Python-Specific Suggestions

- use `asyncio` for streaming model + tool orchestration
- use `pydantic` or typed dataclasses for message and tool schemas
- keep transcript storage append-only where possible
- prefer explicit state machines over ad hoc recursion

## Porting Priority

If building a Python version, first port:

1. query loop
2. tool interface and permission pipeline
3. transcript/session persistence
4. instruction and memory loading
5. tasks and extensions
