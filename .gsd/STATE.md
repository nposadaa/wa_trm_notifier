# STATE.md - Project Memory

> **Current Milestone**: v1.1.0 — Financial Intelligence
> **Current Phase**: Phase 5 — Live Support & Stability (Hotfixes)
> **Sprint**: Bugfix: Deep Clean Destroys IndexedDB
> **Status**: Completed (2026-05-19T13:15:00-05:00)

## Current Position
- **Sprint**: Bugfix: Deep Clean Destroys IndexedDB (Completed & Hardened)
- **Task**: Complete
- **Status**: Released (v1.1.10)

## Last Session Summary
Successfully released v1.1.9 to preserve `IndexedDB` during deep cleans, followed by hotfix v1.1.10. Hotfix v1.1.10 hardens the system against slow-VM behaviors: it prevents duplicate messages by defensively verifying empty composer states when send clicks timeout, and solves false-negative verification crashes by polling the DOM for new message rows for up to 15 seconds. Guided the user through VM updates (`git pull`, clearing `.gsd/needs_maintenance` flag) and performed a local re-authentication and session recovery via the "Zip and Ship" workflow to fully restore the broadcast system on the GCP VM.

## In-Progress Work
- None. Ready for next feature cycle.

## Blockers
- None.

## Context Dump

### Current Hypothesis
- WhatsApp's "offline resume" feature caused the original send failure. The self-healing `deep_clean_profile()` attempted to fix this by deleting caches, but deleted `IndexedDB` which permanently destroyed the session keys.
- **Fix**: Stop deleting `IndexedDB` in `browser_config.py`.

### Files of Interest
- `browser_config.py`: Needs update in `deep_clean_profile()` to preserve `IndexedDB`.
- `.gsd/SPRINT.md`: Contains the sprint details.

## Next Steps
1. **Implement Fix**: Run `/execute` or modify `browser_config.py` to remove `IndexedDB` from the deletion list.
2. **Clear Flag**: Remove the `.gsd/needs_maintenance` flag on the VM.
3. **Zip & Ship**: Re-authenticate locally and transfer the session using the proven zip-and-ship method to restore the VM's broadcasting capability.
