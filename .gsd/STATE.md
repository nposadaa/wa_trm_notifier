# STATE.md — Project Memory

> **Current Phase**: Phase 4 — Cloud Deployment
> **Last Update**: 2026-04-09
> **Status**: Active (resumed 2026-04-12)

## Current Position
- **Phase**: Phase 4 — Cloud Deployment (Stabilization & Documentation)
- **Task**: Final Verification of Cloud Synchronization
- **Status**: Paused at 2026-04-09 20:25 COT. Waiting on user's manual validation of `run_vm.sh`.

## Last Session Summary
- Discovered `auth.py --headless` on GCP VM natively fails primarily due to severe OOM (1GB RAM) crashes during massive E2E decryption.
- Vindicated the "Zip and Ship" strategy. Proven that `--password-store=basic` succeeded in making Windows profiles portable to Linux.
- Fixed catastrophic UI exit in `auth.py` by requiring manual Enter-key closing to prevent database corruption.
- Diagnosed `storage bucket persistence denied` crash on headless Linux Chrome; resolved by injecting a JS mock for `navigator.storage.persist()`.
- Stripped arbitrary background isolation block out of `run_vm.sh`, converting the executable into a synchronous, live-feed runner.

## In-Progress Work
- Execution of synchronous `bash scripts/run_vm.sh` with the fixed `permissions=777` local session dump.

## Blockers
- None. System is primed.

## Context Dump

### Decisions Made
- **Zip and Ship is Canon**: The Cloud Auth VM-native phase is officially deprecated. Transferring Windows sessions is now the core deployment pipeline because VMs cannot handle the multi-gigabyte RAM hit during decryption syncs.
- **Synchronous VM script**: Cron handles backgrounding natively. `run_vm.sh` now streams output linearly using `tee` to provide the user flawless visibility.
- **Navigator Mocking**: Headless Chromium strictly rejects `navigator.storage.persist()`, crashing WhatsApp Web instantly. Masking this with a 1-line JS promise resolution successfully avoids 400 Bad Request death loops.

### Current Hypothesis
Because the storage API crash is circumvented and the Windows profile's filesystem locks have been `chmod` released, the `run_vm.sh` pipeline should fully ingest the `whatsapp_session` flawlessly, find the search-box locator, and broadcast the TRM.

### Exact Start Sequence for Next Session
If the user returns after validation:

**Success Scenario:**
1. Wait for user to confirm the TRM broadcast sent via `run_vm.sh`.
2. Move immediately to configuring `crontab` to trigger `bash scripts/run_vm.sh` daily.

**Failure Scenario:**
1. Run diagnostics sync from local terminal: `.\scripts\fetch-logs.ps1`.
2. Analyze the displayed tail of `logs/vm_run.log` or `logs/notifier_*.log`.
3. Review any downloaded `.png` screenshots in the root directory.
4. Track locator failures or network timeouts based on logs.

## Next Steps
1. Execute `.\scripts\fetch-logs.ps1` to pull today's VM logs.
2. Analyze logs to determine why `run_vm.sh` failed.
3. Finalize Cron logic for autonomous daily runs.
4. Clean handoff for project conclusion.
