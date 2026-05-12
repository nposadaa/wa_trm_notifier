# STATE.md - Project Memory

> **Current Milestone**: v1.1.0 — Financial Intelligence
> **Current Phase**: Phase 5 — Live Support & Stability (Hotfixes)
> **Status**: Paused (2026-05-12T08:24:00-05:00)

## Current Position
- **Phase**: 5 — Live Support & Stability (Hotfixes)
- **Task**: Implement Self-Healing Maintenance Mode (v1.1.5)
- **Status**: Completed at 2026-05-12T08:24:00-05:00

## Last Session Summary
Resolved silent broadcast failures on GCP VM.
- **Maintenance Mode**: Added `.gsd/needs_maintenance` flag to trigger "Deep Clean" (IndexedDB/Service Worker purge) on next run after failure.
- **Hardened Auth**: Increased sync timeout to 30 mins and added localized term detection ("Sincronizando") with emergency reloads.
- **Fixed Notification Bug**: Ensured failure notices retry if the broadcaster fails.
- **Project Rules**: Codified resilience and stability protocols in `PROJECT_RULES.md`.
- **Deployment**: Pushed v1.1.5 to GitHub and verified pull on VM.

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
- `main.py`: Contains v1.1.5 resilience logic and maintenance triggering.
- `broadcaster.py`: Hardened auth loop with sync watchdog.
- `browser_config.py`: Expanded cleanup and deep clean (maintenance) routines.
- `PROJECT_RULES.md`: New canonical rules for TRM Notifier stability.

## Next Steps
1. Monitor the automated 7:00 AM COT run tomorrow.
2. If successful, proceed with Phase 3: Weekly Intelligence (Friday Summaries).
3. Consider automating the cache purge periodically in `run_vm.sh`.

