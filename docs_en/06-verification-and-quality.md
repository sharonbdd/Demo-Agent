# 06. Verification And Quality

## Overview

This codebase assumes that "the model produced an answer" is not enough to claim task success. Quality comes from runtime checks, verification loops, and traceability.

## Built-In Quality Surfaces

The repository includes multiple quality-oriented commands and flows, such as:

- review
- security review
- doctor/runtime diagnostics
- diff/context inspection
- plan and task tracking
- memory editing and instruction management

## Runtime-Level Quality Controls

Quality is also enforced below the command layer:

- tool schema validation
- permission and policy checks
- hook-based interception
- transcript logging
- session recovery
- file history and attribution tracking
- task status transitions

## Context Quality

Poor context is one of the biggest failure sources in agents. The repo addresses that with:

- controlled prompt assembly
- compaction and snipping
- memory deduplication
- selective attachment loading
- path-scoped instruction files

## Verification By Doing

The architecture encourages the agent to verify with tools:

- inspect changed files
- run commands
- read outputs
- update tasks
- report what actually happened

This is a stronger quality strategy than relying on self-evaluation in plain text.

## Traceability

Traceability exists through:

- transcripts
- persisted task outputs
- SDK events
- telemetry
- debug and diagnostic logs

This matters because debugging an agent system usually requires replaying decisions across prompt assembly, tool use, and state transitions.

## Design Lessons

- Quality should be distributed across the stack, not delegated to one "review mode."
- Execution traces are a product feature.
- Verification is best implemented as observable work, not just confidence language.
