# STATE.md - Project Memory

> **Current Milestone**: v1.1.0 — Financial Intelligence
> **Current Phase**: Phase 5 — Live Support & Stability (Hotfixes)
> **Status**: Paused at 2026-05-15T18:40:00-05:00

## Current Position
- **Phase**: 5 — Live Support & Stability (Hotfixes)
- **Task**: Released v1.1.8
- **Status**: Completed at 2026-05-15T18:40:00-05:00

## Last Session Summary
Diagnose the May 15th broadcast skip and fix the timezone drift bug.
- ✅ **Diagnosed False Success**: Manual run previous evening (19:37 COT) executed at 00:37 UTC, writing next day's date to `last_success.date`.
- ✅ **Timezone Fix**: Injected `get_cot_now()` with `America/Bogota` timezone across `main.py` for staleness checking, success tracking, and log naming.
- ✅ **Release Protocol**: Updated `CHANGELOG.md`, `README.md`, `VERSION`, and Git history to package and release `v1.1.8`.

## In-Progress Work
- Released v1.1.8 which completes Backlog Item #6 (Timezone-Aware Date Display).

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
1. **Phase 3**: Weekly Intelligence (Friday Summary feature)
2. **Backlog Item #5**: Refactor legacy broadcaster code
