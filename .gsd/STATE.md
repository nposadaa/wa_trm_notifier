# STATE.md - Project Memory

> **Current Milestone**: v1.1.0 — Financial Intelligence
> **Current Phase**: Phase 5 — Live Support & Stability (Hotfixes)
> **Status**: Active (resumed 2026-05-14T18:10:00-05:00)

## Current Position
- **Phase**: 5 — Live Support & Stability (Hotfixes)
- **Task**: Session Recovery (May 14th Failure)
- **Status**: Paused at 2026-05-14T18:41:00-05:00

## Last Session Summary
Diagnosed the silent May 14th failure.
- ✅ **Root Cause**: Session invalidated (QR Required).
- ✅ **Zip & Ship**: Successfully performed local authentication and transferred session to VM.
- ✅ **Bug Found**: Identified that the `.gsd/needs_maintenance` flag (from a previous failure) was causing the script to "Deep Clean" (delete `IndexedDB`) from the fresh session on every start, triggering a loop.

## In-Progress Work
- No code changes required. 
- Operational fix pending: Remove maintenance flag and re-extract zip on VM.

## Blockers
- None.

## Context Dump
### Decisions Made
- **(DEC-046) Maintenance Hygiene**: Realized that `needs_maintenance` must be manually cleared or the session must be re-extracted AFTER clearing it to avoid the auto-cleanup loop.

### Approaches Tried
- **Manual Log Analysis**: Confirmed `QR Required` error.
- **Zip & Ship**: Successfully transferred folder, but script deleted the database on startup due to the stale flag.

### Current Hypothesis
- Deleting `.gsd/needs_maintenance` on the VM followed by `unzip -o whatsapp_session.zip` will restore full stability.

### Files of Interest
- `main.py`: Entry point where maintenance check happens.
- `browser_config.py`: Contains the `deep_clean_profile()` logic that deletes `IndexedDB`.
- `logs/vm_run.log`: Shows the "Maintenance flag detected" log line.

## Next Steps
1. **VM Cleanup**: Run `rm .gsd/needs_maintenance` on the GCP VM.
2. **Re-extract**: Run `unzip -o whatsapp_session.zip` on the VM.
3. **Catch Up**: Run `bash scripts/run_vm.sh --force` to send today's missed TRM.

