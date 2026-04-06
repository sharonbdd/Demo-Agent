# 03. Skills, Plugins, And MCP

## Overview

The repository has three different extension mechanisms. They overlap, but they are not the same thing.

## 1. Skills

Skills are instruction and workflow units intended to shape model behavior.

Relevant modules:

- `src/skills/bundled/index.ts`
- `src/skills/loadSkillsDir.ts`
- `src/utils/skills/*`

The runtime supports:

- bundled skills shipped with the app
- local skill directories
- skill discovery and usage tracking
- skill-triggered prompt augmentation

Skills are lightweight compared with plugins. They are usually about behavior, guidance, and workflow framing rather than code loading.

## 2. Plugins

Plugins are a broader packaging and distribution mechanism.

Relevant modules:

- `src/utils/plugins/pluginLoader.ts`
- `src/utils/plugins/loadPluginCommands.ts`
- `src/utils/plugins/loadPluginAgents.ts`
- `src/utils/plugins/loadPluginHooks.ts`
- `src/utils/plugins/mcpPluginIntegration.ts`

A plugin can contribute:

- commands
- agents
- hooks
- MCP server definitions
- output styles
- metadata and marketplace packaging

The loader supports:

- cache directories and versioned plugin installs
- seed/plugin base directories
- marketplace-backed plugins
- inline session plugins
- startup checks and validation

## 3. MCP

MCP is the protocol integration layer for external tools, prompts, and resources.

Relevant modules:

- `src/services/mcp/client.ts`
- `src/services/mcp/config.ts`
- `src/services/mcp/types.ts`

The MCP client supports multiple transport types:

- stdio
- SSE
- streamable HTTP
- WebSocket
- SDK-control style connections

The runtime can expose MCP features as:

- callable tools
- listable/readable resources
- prompts and elicitation flows
- authenticated remote integrations

## Why The Three Mechanisms Coexist

### Skills

Best for behavior shaping and reusable workflows.

### Plugins

Best for packaging a bundle of custom capabilities for reuse or distribution.

### MCP

Best for connecting external systems and tools at runtime without hardcoding them into the binary.

## Security And Governance

All three extension mechanisms are subject to policy and settings controls:

- managed settings can restrict customization
- plugin-only policies can limit surfaces
- MCP server allowlists and denylists exist
- hooks and permissions still apply after a capability is loaded

## Design Lessons

- Separate "behavior templates" from "runtime integrations."
- Make extension loading explicit and inspectable.
- Treat externally sourced capabilities as policy-controlled, not trusted by default.
