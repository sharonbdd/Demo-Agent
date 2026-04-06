# 14. Configuration System

## Overview

Configuration in this repo is layered, schema-validated, and policy-aware.

Key modules:

- `src/utils/settings/settings.ts`
- `src/utils/settings/types.ts`
- `src/utils/config.ts`
- `src/bootstrap/state.ts`

## Settings Sources

The runtime merges multiple settings sources, including:

- user settings
- project settings
- local settings
- managed or policy settings
- flag-provided settings
- session-only runtime state

Managed settings can come from platform-specific locations and drop-in directories. This makes the product usable in both personal and enterprise contexts.

## What Can Be Configured

Examples include:

- permissions and additional directories
- hooks
- MCP servers
- skills and agents
- plugin marketplaces
- model and output-style preferences
- sandbox settings
- remote and policy constraints

## Validation Model

The code uses schemas to validate settings while preserving backward compatibility where possible. Invalid fields do not necessarily destroy the whole file; the system tries to keep user configuration editable and recoverable.

## Feature Gates And Environment Variables

The repo uses several dynamic controls beyond JSON settings:

- environment variables
- feature flags via GrowthBook
- session-only toggles in bootstrap state

This is why behavior can vary significantly by build, user, or deployment environment.

## Provider Configuration

The API client supports multiple provider modes, including:

- Anthropic direct API
- Bedrock
- Foundry
- Vertex
- OpenAI-compatible mode through the OpenClaude shim

Provider selection and auth are part of configuration, not hardcoded product identity.

## Design Lessons

- Separate persistent config from session toggles.
- Validate aggressively, but avoid destroying user edits.
- Enterprise policy support must exist beside personal customization, not instead of it.
