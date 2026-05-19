# STATE.md - Project Memory

> **Current Milestone**: v1.1.0 — Financial Intelligence
> **Current Phase**: Phase 5 — Live Support & Stability (Hotfixes)
> **Status**: Paused at 2026-05-19T09:20:18-05:00

## Current Position
- **Phase**: 5 — Live Support & Stability (Hotfixes)
- **Task**: Monitoring 10:00 AM COT CRON run
- **Status**: Paused at 2026-05-19T09:20:18-05:00

## Last Session Summary
Analyzed the May 19 broadcast failure. Confirmed crash was due to a slow WhatsApp "offline resume" hanging the send button click on the VM. Verified the `.gsd/needs_maintenance` flag was correctly set to trigger a deep clean during the 10:00 AM fallback run.

## In-Progress Work
- Monitoring self-healing recovery for May 19 broadcast.

## Blockers
- Waiting for 10:00 AM COT to pass so the VM's secondary CRON job can execute.

## Context Dump

### Decisions Made
- **Wait and Monitor**: Instead of manually intervening, we are letting the built-in self-healing logic (`needs_maintenance` triggering a `deep_clean_profile()`) handle the recovery to prove the system's resilience.

### Current Hypothesis
- WhatsApp's "offline resume" feature causes random internal page reloads on the resource-constrained e2-micro VM, interrupting Playwright interactions. Forcing a deep clean avoids "offline resume" in favor of a "heavy sync", which is slower but more stable.

### Files of Interest
- `logs/vm_run.log` and `logs/notifier_2026-05-19.log`: Need to be checked after 10:00 AM.
- `browser_config.py`: Contains the `deep_clean_profile()` logic.

## Next Steps
1. **Pull Logs**: Run `./scripts/fetch-logs.ps1` after 10:00 AM COT.
2. **Verify Delivery**: Confirm if the 10:00 AM retry successfully sent the message.
3. **Plan Next Move**: If successful, proceed to Phase 3 (Weekly Intelligence). If it fails again, plan a more robust solution for the send button timeout/reload issue.
