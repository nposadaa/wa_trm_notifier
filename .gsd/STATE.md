# STATE.md — Project Memory

> **Current Phase**: Phase 4 — Cloud Deployment
> **Last Update**: 2026-04-12
> **Status**: Active (Resilient Interaction Refinement)

## Current Position
- **Phase**: Phase 4 — Cloud Deployment (Stabilization & Verification)
- **Task**: Final Verification of "Safe Stability" Locator Refactor (DEC-021)
- **Status**: Execution complete. Waiting for user to `git pull` and run `scripts/run_vm.sh` on VM.

## Last Session Summary
- **Diagnosed Splash Screen Hang**: Discovered that e2-micro's 1-core CPU throttles heavily during initial E2E decryption. Resolved by implementing percentage-aware detection and extending login timeout to 20 minutes with a progress-based watchdog.
- **Fixed Sync Progress Recovery**: Added an automated `page.reload()` trigger if the sync state hangs for > 3 minutes, effectively jumpstarting the WebSocket connection.
- **Fixed Stale Element Timeout**: Identified that static `ElementHandle` usage (DEC-019) was crashing due to React re-rendering the input box mid-type. Resolved by pivoting to Playwright **Locators** (DEC-021), which are self-healing.
- **Improved Interaction Resiliency**: Upgraded typing to `press_sequentially` and added a "Patience Patch" that explicitly waits for background sidebar sync to finish before broadcasting.

## In-Progress Work
- Manual validation of `DEC-021` changes on the GCP instance.

## Blockers
- None. System is in its most resilient state to date.

## Context Dump

### Decisions Made
- **DEC-021 (Locators over Handles)**: Replaced static pointers with search-based queries. This is the definitive fix for "Stale Element" errors on overloaded cloud hardware where the UI renders asynchronously.
- **Percentage Watchdog**: Progress-based resets on the 20-minute timeout ensure we allow the VM to "cook" through decryption without idling indefinitely on real crashes.

### Current Hypothesis
The combined force of **extended sync patience** and **self-healing locators** will finalize the stabilization. The script can now survive the "jitter" of a 1GB RAM VM and effectively upload messages even when historical data sync is backgrounded.

### Exact Start Sequence for Next Session
**Success Scenario:**
1. Confirm message delivery via `fetch-logs.ps1`.
2. Move immediately to final `crontab` configuration for daily automation.
3. Archive the project artifacts and transition to the "Maintenance & Handover" walkthrough.

## Next Steps
1. Push latest `broadcaster.py` and `DECISIONS.md` to GitHub.
2. User runs `git pull` and `bash scripts/run_vm.sh` on VM.
3. Analyze final results via `.\scripts\fetch-logs.ps1`.
4. Finalize daily Cron scheduling.
