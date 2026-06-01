# STATE.md - Project Memory

> **Current Milestone**: v1.1.0 — Financial Intelligence
> **Current Phase**: Phase 5 — Live Support & Stability (Hotfixes)
> **Sprint**: Hotfix: Session Decryption Sync Resilience (v1.1.14)
> **Status**: Released at 2026-06-01T09:30:00-05:00

## Current Position
- **Sprint**: Hotfix: Session Decryption Sync Resilience (v1.1.14)
- **Task**: Complete
- **Status**: Released (v1.1.14)

## Last Session Summary
Successfully released v1.1.14 to resolve a critical session decryption hang on the slow GCP VM. During the Monday morning (June 1st) run, the WhatsApp Web session decryption stalled under heavy CPU load, getting stuck at 59% sync progress. Because the existing watchdog timer was designed to abort execution immediately after 5 minutes of no progress, the entire run failed.
We resolved this by:
1. Enhancing the 5-minute inactivity watchdog in `broadcaster.py` to trigger a `safe_reload` and reset the progress tracker instead of aborting the run. This allows multiple recovery attempts within the 30-minute maximum initial wait window.
2. Fixing a bug where the progress recovery reload checked overall elapsed script time instead of the time spent stuck at the current percentage, making the reload guard behave correctly under normal slow decryption.

All local dry runs passed, and the hotfix is packaged and ready for VM deployment.

## In-Progress Work
- None. Ready for VM pull and manual recovery run.

## Blockers
- None.

## Context Dump

### Current Hypothesis
- Enabling safe reloads during stuck decryption phases in the state-aware loop allows virtualized browsers on throttled CPU hardware to naturally recover WebSocket and database locks, ensuring successful login completion within the extended 30-minute window.

### Files of Interest
- `broadcaster.py`: Hardened session sync loop watchdog and stuck percentage recovery.
- `CHANGELOG.md`: Logged modifications under version v1.1.14.
- `VERSION`: Bumped to v1.1.14.

## Next Steps
1. **Pull to VM**: Pull v1.1.14 on the GCP VM and run the broadcaster (or let the scheduled 10:00 AM COT cron fallback execute it).
2. **Phase 3 Weekly Summary Message**: Resume implementing the Friday Weekly Summary Message feature.
