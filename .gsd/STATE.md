# STATE.md - Project Memory

> **Current Milestone**: v1.1.0 — Financial Intelligence
> **Current Phase**: Phase 5 — Live Support & Stability (Hotfixes)
> **Status**: Active (resumed 2026-05-11T10:55:17-05:00)

## Current Position
- **Phase**: 5 — Live Support & Stability (Hotfixes)
- **Task**: Implement Resilient Scheduling & API Fallback Notifications
- **Status**: Paused at 2026-05-11T13:45:00-05:00

## Last Session Summary
Diagnosed persistent broadcast failures on the GCP VM (Friday downtime and Monday sync timeout).
- **Resilient Scheduling**: Added a secondary "self-healing" CRON run at 15:00 UTC (10:00 AM COT).
- **Success Tracking**: Implemented `last_success.date` to prevent double-posting.
- **API Failure Notifications**: Added logic to notify the WhatsApp group when the TRM API is down.
- **Session Cleanup**: Performed hard purge of browser cache on VM to resolve sync hangs.

## In-Progress Work
- None (All resilience features deployed and verified via manual test run).

## Blockers
- None.

## Context Dump
### Decisions Made
- **(DEC-044) Success Tracking**: Used a simple date file (`.gsd/last_success.date`) to manage multiple CRON runs without a complex database.
- **(DEC-045) Proactive Failure Notice**: Decided to send a "API Down" message to the group to manage user expectations during government outages.

### Current Hypothesis
- The "SYNCING..." hang is likely caused by the extreme memory constraints (1GB) of the e2-micro VM when the WhatsApp profile bloat reaches a certain threshold. Regular purging is required.

### Files of Interest
- `main.py`: Contains the new resilient logic and failure notification blocks.
- `scripts/run_vm.sh`: Triggered twice daily by the updated VM crontab.

## Next Steps
1. Monitor the automated 7:00 AM COT run tomorrow.
2. If successful, proceed with Phase 3: Weekly Intelligence (Friday Summaries).
3. Consider automating the cache purge periodically in `run_vm.sh`.

