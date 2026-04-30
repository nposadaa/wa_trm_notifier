# STATE.md - Project Memory

> **Current Phase**: Phase 5 - Operations (Post-Sprint 5)
> **Last Update**: 2026-04-25
> **Status**: Active (resumed 2026-04-30T09:55:00-05:00)

## Current Position
- **Phase**: Phase 5 - Operations
- **Task**: Monitoring v1.0.7
- **Status**: Paused at 2026-04-25T12:41:00-05:00

## Last Session Summary
- **Fresh Session Deployed**: Zip & Ship completed — cleared 531MB bloated session on VM and replaced with a fresh ~65MB session from local auth.
- **Manual Test Passed**: `run_vm.sh` executed successfully on VM with the new session — message delivered.
- **CRON Re-enabled**: Crontab uncommented and active on the VM.
- **GitHub Release v1.0.7**: Created on GitHub.
- **Docs Updated**: README sprint status updated to v1.0.7, CHANGELOG v1.0.6 header fixed, v1.0.7 tag converted to annotated and pushed.

## In-Progress Work
- None (All changes pushed to master and deployed to VM).

## Blockers
- None. All blockers resolved.

## Context Dump
### Decisions Made
- **Zip & Ship over VM auth**: Confirmed again as the reliable authentication method — avoids e2-micro OOM crashes during E2E decryption.
- **Jumpstart Reload**: 30s timeout on connectivity banners triggers page reload for WebSocket reconnection.
- **Recovery Reload**: 60s outbox watchdog reloads the page if a message is stuck with a clock icon.

### Approaches Tried
- **Verification normalisation**: Normalised emoji handling in row-anchored checks to prevent false-negative warnings.

## Next Steps
1. **Monitor CRON**: Confirm tomorrow's run succeeds with the new auto-bloat cleanup.
2. **Observe Profile Growth**: Check if 269MB was an anomaly or a trend.
