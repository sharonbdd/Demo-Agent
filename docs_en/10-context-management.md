# 10. Context Management

## Overview

This repository treats context as a scarce runtime resource. Context management is distributed across prompt assembly, memory loading, compaction, and result truncation.

## Context Sources

Major context sources include:

- conversation history
- system context
- `CLAUDE.md` instructions
- typed memory
- attachments
- skill injections
- MCP resources and tool descriptions
- plugin-provided instructions

## Why Context Needs Management

Without control, the agent would drift toward:

- oversized prompts
- repeated instruction injection
- poor cache hit rates
- hidden contradictions between old and new state

## Techniques Used In The Repo

### Cached context sections

Some sections are memoized or cached per session to avoid repeated expensive computation.

### Selective loading

Not all persistence is injected every turn. The runtime chooses what to attach or discover.

### Compaction

The query layer includes auto-compaction and reactive compaction paths for long sessions.

### Snipping and projection

Feature-gated snip/collapse systems let the runtime project a smaller working history without deleting durable transcript truth.

### Truncation safeguards

Memory entrypoints, MCP descriptions, and other large payloads are explicitly capped.

## Practical Principle

The system separates three ideas:

- what exists on disk
- what is visible in the active transcript
- what is sent to the model this turn

That separation is what makes long-running agent sessions feasible.

## Design Lessons

- Persist broadly, inject narrowly.
- Make context loading incremental and debuggable.
- Keep prompt-size defenses close to the query loop, not only in the UI.
