# STATE.md - Project Memory

> **Current Milestone**: v1.1.0 — Financial Intelligence
> **Current Phase**: Phase 5 — Live Support & Stability (Hotfixes)
> **Status**: Paused (2026-05-12T08:24:00-05:00)

## Current Position
- **Phase**: 5 — Live Support & Stability (Hotfixes)
- **Task**: Stability Hotfixes (v1.1.5 - v1.1.7)
- **Status**: Paused at 2026-05-12T12:50:00-05:00

## Last Session Summary
Resolved delivery reliability issues and hardened the broadcaster for v1.1.7.
- ✅ **Verification Fix**: Prevented false-positive success by re-verifying message text after reloads.
- ✅ **Input Hardening**: Implemented robust composer clearing and typing verification.
- ✅ **Crash Fix**: Resolved a critical `NameError` (missing import) in the diagnostic logic.
- ✅ **Manual Recovery**: Successfully executed a forced broadcast on the VM, delivering today's TRM.

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
1. **Resume Development**: Pivot to **Phase 3: Weekly Intelligence** (Friday summaries).
2. **Monitor Logs**: Ensure the automated 7:00 AM COT run tomorrow functions correctly without manual intervention.
3. **Maintenance**: Periodically check logs for "Maintenance Triggered" events to confirm self-healing is active.

