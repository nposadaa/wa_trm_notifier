# STATE.md - Project Memory

> **Current Milestone**: v1.1.0 — Financial Intelligence
> **Current Phase**: Phase 5 — Live Support & Stability (Hotfixes)
> **Status**: Paused (2026-05-12T08:24:00-05:00)

## Current Position
- **Phase**: 5 — Live Support & Stability (Hotfixes)
- **Task**: Fix False-Positive Verification & Stale Composer (v1.1.6)
- **Status**: Completed at 2026-05-12T12:15:00-05:00

## Last Session Summary
Resolved "False Success" bug where stale rows triggered delivery verification.
- **Hardened Verification**: Re-verifies text in every poll loop to prevent matching previous day's messages during recovery.
- **Robust Clear**: Added multi-pass composer clearing with JS fallback to prevent "Enter" sending old drafts.
- **Force Flag**: Added `--force` to `main.py` for manual override of successful runs.
- **Timestamped Diags**: Screenshots now include HHMM to distinguish between runs.

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

