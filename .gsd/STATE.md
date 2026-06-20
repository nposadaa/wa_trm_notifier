# STATE.md - Project Memory

> **Current Milestone**: v1.1.0 — Financial Intelligence
> **Current Phase**: Phase 5 — Live Support & Stability (Hotfixes)
> **Sprint**: Hotfix: Failure Loop Break & VM Search Stabilization (v1.1.15)
> **Status**: Active (resumed 2026-06-20T09:06:46-05:00)

## Current Position
- **Phase**: Phase 5 — Live Support & Stability (Hotfixes)
- **Task**: Complete
- **Status**: Active (resumed 2026-06-20T09:06:46-05:00)

## Last Session Summary
Implemented hotfix version v1.1.15 to resolve the 3-day broadcast failure loop on the VM. Modified the browser configuration to clear `.gsd/needs_maintenance` immediately upon deep clean execution. Implemented a post-deep-clean settling window in `broadcaster.py` to allow the chat index list to populate before starting searches. Dynamicized the search attempt limits, added search diagnostics to log visible chat rows, and updated the return signature of `run_broadcaster` to prevent transient search or verification failures from triggering deep cleans. Verified all changes locally with a dry run and mocked maintenance trigger.

## In-Progress Work
- None.

## Blockers
- None.

## Context Dump

### Current Hypothesis
- Clearing the maintenance flag immediately after deep cleaning prevents infinite deep-clean loops. Adding a post-deep-clean settling window (polling for visible chat rows) and increasing the search attempts to 10 dynamically allows the slow e2-micro VM sufficient time to rebuild the chat list and index before searching.

### Files of Interest
- `browser_config.py`: Returns deep clean status, clears flag.
- `broadcaster.py`: Implements settling loop, dynamic search, and return signature tuple.
- `main.py`: Handles tuple unpacking, writes flag conditionally.
- `CHANGELOG.md`: Logged modifications under version v1.1.15.
- `VERSION`: Bumped to v1.1.15.

## Next Steps
1. **Pull to VM**: Run `git pull origin master` on the GCP VM to fetch the v1.1.15 hotfix.
2. **Execute on VM**: Clear VM maintenance flag (`rm -f .gsd/needs_maintenance`) and run the broadcaster using `bash scripts/run_vm.sh --force` (or wait for the scheduled cron).
3. **Phase 3 Weekly Summary Message**: Start implementing the Friday Weekly Summary Message feature.
