# 15. MVP Scope

## If You Were Rebuilding A Smaller Version

This repository is larger than an MVP. A practical MVP should copy the architecture shape, not the full feature count.

## Phase 1: Minimal Useful Agent

Build these first:

- CLI entrypoint
- one provider-backed model client
- dynamic system/user context assembly
- core tools: read, write, edit, grep/glob, shell
- permission modes: allow, ask, deny
- transcript persistence and resume
- a small command surface

Without these, the result is still mostly a chatbot.

## Phase 2: Robust Agent Runtime

Next add:

- tool progress and structured results
- task model for background work
- compaction/context controls
- `CLAUDE.md`-style instruction discovery
- typed durable memory
- hooks

This is where the product becomes operationally reliable.

## Phase 3: Ecosystem And Scale

Then add:

- plugins
- MCP
- subagents and teammate modes
- remote/bridge control
- marketplace and policy management

These features are valuable, but they are force multipliers for a runtime that already works.

## What Not To Cut Too Aggressively

Even in an MVP, do not skip:

- explicit permissions
- transcript persistence
- schema-validated tools
- context budgeting

Those are foundational, not premium add-ons.
