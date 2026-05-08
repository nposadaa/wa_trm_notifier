# STATE.md - Project Memory

> **Current Milestone**: v1.1.0 — Financial Intelligence
> **Current Phase**: Phase 5 — Live Support & Stability (Hotfixes)
> **Status**: Paused at 2026-05-08T14:50:00-05:00

## Current Position
- **Milestone**: v1.1.0 — Financial Intelligence
- **Phase**: 3 (Next Up)
- **Task**: between tasks
- **Status**: Paused

## Last Session Summary
Diagnosed and fixed a critical delivery failure where messages were sent to the wrong chat. The broadcaster's text fallback search logic was removed because it was clicking previous messages instead of the group chat. Increased exact match timeouts. Deployed `v1.1.3`.

## In-Progress Work
- None

## Blockers
- None.

## Context Dump
### Decisions Made
- **(DEC-042) Strict Chat Matching**: Removed `get_by_text` fallback search. It's too dangerous because it can match past messages and send broadcasts to the wrong recipients. Increased exact match timeout to 8s instead.

### Files of Interest
- `broadcaster.py`: Search timeout and fallback logic.

## Next Steps
1. /plan 3 — Weekly Intelligence
