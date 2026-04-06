# docs_en

This directory documents how the agent system in this repository actually works today.

The codebase is not a minimal "chat + tools" demo. It is a full agent runtime built around:

- dynamic prompt assembly
- model/provider abstraction
- a typed tool system with permissions and hooks
- persistent instructions and memory
- transcript-backed sessions and resume
- slash commands and interactive TUI flows
- background tasks, subagents, and remote/bridge operation
- plugins, skills, MCP servers, and feature-gated extensions

## What Changed

The previous version of these docs read more like a speculative product-requirements document. The updated version is grounded in a code review of the current repository, especially:

- `src/main.tsx`
- `src/query.ts`
- `src/QueryEngine.ts`
- `src/tools.ts`
- `src/services/tools/*`
- `src/utils/permissions/*`
- `src/utils/claudemd.ts`
- `src/memdir/*`
- `src/utils/sessionStorage.ts`
- `src/utils/plugins/*`
- `src/services/mcp/*`
- `src/bridge/*`
- `src/tasks/*`
- `src/utils/settings/*`

## Reading Order

If you want a fast mental model, read in this order:

1. `00-product-overview.md`
2. `07-architecture-map.md`
3. `08-agent-runtime-loop.md`
4. `02-tools-permissions-and-execution.md`
5. `04-memory-and-session.md`
6. `03-skills-plugins-mcp.md`
7. `14-configuration-system.md`

## Scope

These docs describe the current TypeScript/Bun/Node implementation. A few files keep Python-oriented notes because the repository also contains Python experiments and the architecture is portable, but the production runtime here is the TypeScript stack.

## Conventions

- "Agent" means the full runtime, not just the model.
- "Session" means the persisted conversation and runtime state for a working thread.
- "Memory" means durable instruction/persistence layers, not just token context.
- "Bridge" means remote-control/session-ingress connectivity.
- "MCP" means Model Context Protocol servers, tools, prompts, and resources.

## File Guide

- `00`-`06`: product and runtime behavior
- `07`-`14`: architecture, state, context, failure, and configuration
- `15`-`16`: implementation guidance for a smaller or alternate-language build
- `FEATURE_AUDIT.md`: codebase capability/gap audit derived from the docs set
