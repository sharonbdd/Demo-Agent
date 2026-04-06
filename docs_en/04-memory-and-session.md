# 04. Memory And Session

## Overview

This repository uses several kinds of persistence. They should not be conflated.

## Instruction Memory: `CLAUDE.md`

`src/utils/claudemd.ts` discovers instruction files from multiple scopes:

- managed/global instructions
- user instructions
- project instructions
- local private project instructions

Features include:

- ordered precedence
- traversal up the directory tree
- support for `.claude/rules/*.md`
- `@include` expansion
- frontmatter path scoping

This layer is primarily about instruction injection, not user memory recall.

## Typed Durable Memory: `MEMORY.md` And Memory Files

The `src/memdir/*` subsystem is a second persistence layer with a stronger structure.

It provides:

- a dedicated memory directory
- a typed memory taxonomy
- indexed memory entrypoints
- explicit save/update/delete guidance
- truncation guards for oversized memory indexes

This subsystem is meant for durable cross-session recall, not just repo instructions.

## Transcript-Backed Session Storage

`src/utils/sessionStorage.ts` persists session transcripts, subagent logs, metadata, and resumable state.

Important properties:

- JSONL transcript storage
- distinction between durable transcript messages and ephemeral progress
- separate paths for main sessions and subagents
- support for resume, search, naming, and session lineage

## Session Resume

Resume is supported because the code treats session persistence as core infrastructure:

- messages can be loaded back into state
- parent/child chains are reconstructed carefully
- stale or ephemeral messages are filtered
- task and transcript artifacts are separated

## Compaction And Long-Context Management

The repo also includes compaction and snipping systems. Session state is persistent, but prompt state is still budgeted. So persistence and in-context visibility are intentionally decoupled.

## Design Lessons

- Separate instruction memory from durable personal/project memory.
- Persist enough structure to resume safely, not just raw chat text.
- Avoid treating progress UI events as transcript truth.
- Design memory systems around update/delete as much as append.
