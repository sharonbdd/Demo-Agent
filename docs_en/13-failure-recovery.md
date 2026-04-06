# 13. Failure Recovery

## Overview

The repository contains explicit recovery logic across API calls, tool execution, session persistence, and bridge connectivity.

## Main Failure Classes

### API and model failures

Handled through retry logic, fallback paths, token-limit recovery, and compaction.

### Tool failures

Handled through structured tool errors, synthetic result generation when needed, and progress-aware cleanup.

### Permission denials

Handled as part of normal control flow rather than a crash. The session can keep going with an adjusted plan.

### Session persistence issues

Transcript code contains guards against oversized files, stale progress entries, and chain corruption.

### Bridge and transport failures

Remote control code includes:

- heartbeat loops
- reconnect flows
- token refresh schedulers
- auth-expiry recovery
- session archival/cleanup

## Recovery Philosophy

The codebase generally prefers:

- recover if the session can continue safely
- preserve traceability of what failed
- avoid silently mutating durable history into something misleading

## Examples In The Code

- `src/query.ts` for compaction and token-limit recovery
- `src/services/tools/StreamingToolExecutor.ts` for sibling cancellation and fallback handling
- `src/utils/sessionStorage.ts` for transcript repair and guarded loading
- `src/bridge/*` and `src/cli/transports/*` for reconnect logic

## Design Lessons

- Long-running agents need explicit failure classes, not a generic catch-all.
- Recovery should preserve auditability.
- Remote transports need the same rigor as tool execution.
