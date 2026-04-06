# 12. Workspace And Isolation

## Overview

The runtime tracks workspace boundaries carefully because tool safety, memory discovery, and session persistence all depend on path correctness.

## Core Workspace Concepts

### Original cwd vs current cwd

The bootstrap layer tracks stable project identity separately from the mutable working directory used by tools.

### Additional working directories

Permissions can include extra allowed directories beyond the initial workspace.

### Project root and worktree support

The code distinguishes project identity from worktree execution paths and supports worktree-aware flows.

## Isolation Mechanisms

### Permission-scoped filesystem access

The permission system decides what directories and operations are allowed.

### Sandbox-aware execution

Shell tools can run with sandbox logic and explicit override paths.

### Session-specific storage

Transcripts, task outputs, and subagent logs are stored per session/project path.

### Remote/session-ingress isolation

Bridge-connected sessions have their own connection state, tokens, and remote transport handling.

## Why Isolation Is Hard In Agent Systems

An agent is constantly crossing boundaries:

- reading repo files
- writing generated changes
- touching user home or temp directories
- invoking external tools
- entering worktrees or remote sessions

If path and session identity are sloppy, persistence and permission bugs follow quickly.

## Design Lessons

- Separate project identity from momentary execution location.
- Carry path rules into permissions, memory loading, and persistence.
- Treat remote mode as a different isolation surface, not just another transport.
