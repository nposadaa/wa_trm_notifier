# STATE.md - Project Memory

> **Current Milestone**: v1.1.0 — Financial Intelligence
> **Current Phase**: Phase 5 — Live Support & Stability (Hotfixes)
- **Sprint**: Hotfix: Non-Destructive Outbox Polling & Connection Stabilization (v1.1.27)
- **Status**: Paused at 2026-08-26T13:57:00-05:00

## Current Position
- **Phase**: Phase 5 — Live Support & Stability (Hotfixes)
- **Task**: VM Broadcast Execution & Verification of v1.1.27
- **Status**: Paused (v1.1.27 Live on GitHub origin/master)

## Last Session Summary
- Resumed session, fetched logs, and analyzed recent VM execution failures.
- Confirmed VM session was logged out/invalidated on Aug 17.
- User performed local authentication (`auth.py`) and Zip-n-Ship transfer to GCP VM (`trm-notifier`).
- Investigated post-zip-n-ship broadcast runs:
  - First run: Login succeeded! Search succeeded. Send button click timed out; Enter fallback was missing and DOM virtualization caused a false-empty composer assumption.
  - Released `v1.1.26`: Added Enter key fallback and initialized `is_stuck_in_outbox` in verification scope.
  - Second run: Message dispatched into DOM, but showed Clock icon (`🕒` / outbox pending). The code triggered a destructive `safe_reload(page)` after 60s, destroying the in-flight WebSocket connection and causing HTTP 410 errors.
  - Released `v1.1.27`: Removed destructive page reload during outbox polling, extended verification deadline to 300s (5m), and added 15s post-sync socket stabilization. Updated README.md and release protocol rules.
  - Tested test suite (`pytest` 3/3 passed) and pushed `v1.1.27` commit and tag to GitHub `origin/master`.

## In-Progress Work
- None. Working tree is clean. `v1.1.27` is live on GitHub `origin/master`.

## Blockers
- None.

## Context Dump

### Decisions Made
- `DEC-030`: Outbox pending state (`🕒`) on slow e2-micro VMs must NOT trigger page reloads, as reloading the page destroys active WebSockets and triggers HTTP 410 errors. Instead, poll for up to 300s to allow normal network flush.
- `DEC-031`: Mandatory release protocol checklist strictly requires updating `README.md` version banner alongside `VERSION` and `CHANGELOG.md`.

### Files of Interest
- `broadcaster.py`: Broadcaster engine logic & non-destructive delivery verification (v1.1.27).
- `VERSION`: `1.1.27`.
- `README.md`: Updated with `v1.1.27` version banner.
- `CHANGELOG.md`: Full release history.

## Next Steps
1. On the GCP VM, pull the latest code: `git pull origin master`
2. Clear any lingering maintenance/success flags: `rm -f .gsd/last_success.date .gsd/needs_maintenance`
3. Execute the broadcast manually: `bash scripts/run_vm.sh --force`
4. Confirm message delivery in the WhatsApp group.
