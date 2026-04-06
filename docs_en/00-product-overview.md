# 00. Product Overview

## Summary

This repository implements an AI coding runtime, not just a chat interface. The model is one component inside a larger operating loop that assembles context, selects tools, enforces permissions, persists state, spawns tasks, and recovers from failure.

## What The Product Is

At a practical level, the system combines:

- a CLI and TUI entrypoint
- a provider-abstracted LLM client
- a multi-turn query engine
- typed tools with schema validation
- permissions, policy rules, and hooks
- persistent instruction layers (`CLAUDE.md`, `MEMORY.md`, settings, plugins)
- background tasks and subagents
- optional remote/bridge control
- extension surfaces for skills, plugins, and MCP servers

## Primary User Jobs

The runtime is designed for users who want the agent to do engineering work, not only describe it:

- inspect and change code
- run commands and verify results
- manage context across long sessions
- delegate work to subagents or background tasks
- attach organization-specific instructions and policies
- integrate external systems through MCP or plugins
- resume and audit work after interruptions

## Core Product Properties

### 1. The model is embedded in an execution system

The codebase centers on a loop in `src/query.ts` and `src/QueryEngine.ts`, not on a single request/response API call.

### 2. Context is assembled, not static

Prompt content comes from multiple layers:

- system context such as git state and session metadata
- user context such as `CLAUDE.md`
- memory instructions from the typed memory system
- MCP, plugin, and skill injections
- output-style, thinking, and settings-dependent instructions

### 3. Tool execution is governed

Tool calls are schema-validated, permission-checked, hook-aware, and tracked. High-risk tools like shell execution have stricter handling than passive tools like file reads.

### 4. State persists across turns

The system stores transcripts, session metadata, task outputs, and memory files. Resume is a first-class workflow, not an afterthought.

### 5. The platform is extensible

The base runtime can be extended by:

- bundled and local skills
- local and marketplace plugins
- MCP servers over stdio, SSE, HTTP, WebSocket, or SDK control transports

## Deployment Surfaces

The current repository supports several operating modes:

- interactive local CLI/TUI
- SDK/headless query execution
- background task execution
- subagent and teammate execution
- remote control / bridge-connected sessions
- provider-switched deployments, including OpenAI-compatible mode via `src/services/api/openaiShim.ts`

## Why This Matters For AI Agents

The main design lesson from this repository is that a useful engineering agent is mostly runtime architecture:

- prompt assembly
- state and context management
- permissioning
- tool orchestration
- extensibility
- recovery

The base model quality matters, but the product behavior mostly comes from the runtime around it.
