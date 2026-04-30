# STATE.md - Project Memory

> **Current Phase**: Phase 5 - Operations (Post-Sprint 5)
> **Last Update**: 2026-04-30
> **Status**: Paused at 2026-04-30T10:45:00-05:00

## Current Position
- **Phase**: Phase 5 - Operations
- **Task**: Maintenance (v1.0.8 Released)
- **Status**: Paused at 2026-04-30T10:45:00-05:00

## Last Session Summary
- **v1.0.8 Released**: Bumper version, tagged on GitHub, and pushed to master.
- **Auto-Bloat Cleanup**: Implemented automatic clearing of browser cache/code-cache to save ~200MB RAM on launch.
- **Verification Hardened**: Stripped emojis from matching logic to prevent false-negative delivery verification on slow VMs.
- **Xvfb Startup Fix**: Added lock cleanup to `run_vm.sh` to prevent startup hangs.
- **Confirmed Successful Run**: Manually verified a broadcast on the VM with the new fixes; acknowledgment time dropped from 345s to 39s.

## In-Progress Work
- None. All fixes committed, tagged, and deployed to VM.

## Blockers
- None. All blockers resolved.

## Context Dump
### Decisions Made
- **(DEC-035) Auto-Cache Clearing**: Decided to delete `Cache` and `Code Cache` on every launch to keep the e2-micro RAM usage below the 1GB threshold.
- **(DEC-036) Emoji Neutrality**: Decided to strip non-ASCII from verification snippets to overcome rendering inconsistencies in headless/low-resource browsers.

### Approaches Tried
- **Manual verification**: Confirmed that message presence check fails if emojis are missing from `inner_text()` but passes if stripped.

## Next Steps
1. **Monitor CRON**: Confirm tomorrow's run succeeds autonomously with the new v1.0.8 cleanup logic.
2. **Cleanup Local Artifacts**: Remove stale `.png` diagnostics from the local project root.
