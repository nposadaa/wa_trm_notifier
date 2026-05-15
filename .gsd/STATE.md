# STATE.md - Project Memory

> **Current Milestone**: v1.1.0 — Financial Intelligence
> **Current Phase**: Phase 5 — Live Support & Stability (Hotfixes)
> **Status**: Paused at 2026-05-14T19:52:00-05:00

## Current Position
- **Phase**: 5 — Live Support & Stability (Hotfixes)
- **Task**: None (between tasks)
- **Status**: Paused at 2026-05-14T19:52:00-05:00

## Last Session Summary
Completed May 14th Session Recovery via fresh Zip & Ship. No code changes.
- ✅ **Root Cause**: Session invalidated (QR Required) + maintenance flag loop destroyed fresh sessions.
- ✅ **Fix**: Fresh local auth → zip → clean VM (rm flag + rm old session) → transfer → unpack → `--force` run.
- ✅ **Broadcast Delivered**: Today's TRM successfully sent.
- ⚠️ **New Bug Found**: Message displayed May 15 date instead of May 14 (UTC vs COT timezone mismatch). Added to BACKLOG as item #6.

## In-Progress Work
- None. No code changes made — operational fix only.

## Blockers
- None.

## Context Dump
### Decisions Made
- **(DEC-046) Maintenance Hygiene**: `needs_maintenance` flag MUST be cleared on VM BEFORE extracting a fresh Zip & Ship session, or the deep_clean will destroy the transferred IndexedDB on first run.
- **(DEC-047) Zip & Ship Order of Operations**: Always: (1) rm flag, (2) rm old session, (3) unzip fresh, (4) chmod 777, (5) run immediately.

### Files of Interest
- `BACKLOG.md`: Item #6 — Timezone-Aware Date Display (High priority)
- `main.py`: Staleness check uses `datetime.now()` (UTC on VM) — needs `America/Bogota`
- `browser_config.py`: Already sets `timezone_id="America/Bogota"` for the browser, but Python code is unaware

## Next Steps
1. **Backlog Item #6**: Fix timezone-aware date display in `main.py`
2. **Phase 3**: Weekly Intelligence (Friday Summary feature)
3. **Backlog Item #5**: Refactor legacy broadcaster code
