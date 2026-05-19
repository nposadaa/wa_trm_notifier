# STATE.md - Project Memory

> **Current Milestone**: v1.1.0 — Financial Intelligence
> **Current Phase**: Phase 5 — Live Support & Stability (Hotfixes)
> **Sprint**: Bugfix: Deep Clean Destroys IndexedDB
> **Status**: Paused at 2026-05-19T11:12:18-05:00

## Current Position
- **Sprint**: Bugfix: Deep Clean Destroys IndexedDB
- **Task**: Todo
- **Status**: Paused at 2026-05-19T11:12:18-05:00

## Last Session Summary
Analyzed the failed 10:00 AM fallback broadcast. Confirmed that `deep_clean_profile()` is lethal to modern WhatsApp Web sessions because it deletes `IndexedDB`, which now holds critical encryption keys. This caused a `Session Invalidated! (QR Required)` error. Packaged the fix into a new Sprint.

## In-Progress Work
- Ready to start Sprint 1: Bugfix: Deep Clean Destroys IndexedDB.

## Blockers
- None. Ready for execution upon resuming.

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
