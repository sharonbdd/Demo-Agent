# 01. System Prompt And Orchestration

## Overview

The prompt is dynamically assembled per session and per turn. The code does not treat the system prompt as one static string.

Key modules:

- `src/context.ts`
- `src/utils/queryContext.ts`
- `src/utils/messages/systemInit.ts`
- `src/query.ts`
- `src/QueryEngine.ts`
- `src/bootstrap/state.ts`

## Prompt Inputs

### System context

`src/context.ts` builds cached system context such as:

- git branch
- main branch
- git status snapshot
- recent commits
- optional cache-breaking/debug injections

### User context

The user context layer can inject:

- discovered `CLAUDE.md` instructions
- date information
- additional instruction files discovered from workspace traversal

### Memory prompt

The typed memory subsystem in `src/memdir/*` contributes behavioral guidance and durable recall instructions. This is distinct from `CLAUDE.md`.

### Dynamic mode-dependent instructions

The runtime may alter prompt construction based on:

- fast mode
- thinking configuration
- plan mode
- output style
- selected model
- interactive vs headless session
- subagent role
- feature flags

### Extension-driven instructions

Skills, plugins, and MCP connections can add instructions or make additional capabilities visible to the model.

## Why Orchestration Exists

The codebase solves three prompt problems that simple agent demos usually ignore.

### 1. Environment grounding

The model needs project reality, not just the last user message.

### 2. Role specialization

Main-thread agents, subagents, teammates, and bridge-connected sessions do not always need the same prompt envelope.

### 3. Context economy

Large static prompts are too expensive. This repo uses caching, on-demand injection, compaction, and turn-aware assembly to keep the prompt useful without always sending everything.

## Orchestration Pattern

At a high level, each turn follows this shape:

1. gather cached and live context
2. normalize messages
3. append system and user context
4. apply mode- and feature-specific instructions
5. call the model
6. interpret tool requests and continue the trajectory

## Practical Design Lessons

- Treat prompt construction as a subsystem, not a template.
- Keep persistent instructions separate from turn-local reasoning.
- Differentiate "always include" content from "load on demand" content.
- Cache expensive context when safe, but expose enough state to invalidate it.
