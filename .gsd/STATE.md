# STATE.md - Project Memory

> **Current Milestone**: v1.1.0 — Financial Intelligence
> **Current Phase**: Phase 5 — Live Support & Stability (Hotfixes)
- **Sprint**: Hotfix: Outbox Hang Root-Cause Fix & SOFT SUCCESS Guard (v1.1.28)
- **Status**: Ready for Deployment (v1.1.28)

## Current Position
- **Phase**: Phase 5 — Live Support & Stability (Hotfixes)
- **Task**: VM Broadcast Execution & Verification of v1.1.28
- **Status**: Ready for Deployment

## Last Session Summary
- Diagnosed root causes of persistent outbox hangs (`🕒`) and false-positive SOFT SUCCESS reports from Aug 28 logs:
  - `clean_browser_bloat()` was deleting `Service Worker/CacheStorage` and `Service Worker/ScriptCache` on every run, destroying WhatsApp Web's background sync engine and triggering offline-resume timeouts.
  - `--disable-background-networking` flag in Chromium launch arguments suppressed WebSocket background sync.
  - DOM row-drift during verification loop reset `is_stuck_in_outbox`, allowing `SOFT SUCCESS` to fire on messages that were clearly stuck in outbox.
- Released `v1.1.28`:
  - Preserved Service Worker caches in `browser_config.py`.
  - Removed `--disable-background-networking` flag from `browser_config.py`.
  - Added pre-type `navigator.onLine` health check in `broadcaster.py`.
  - Added sticky `outbox_ever_detected` flag to permanently block `SOFT SUCCESS` on hung outbox messages.
  - Added non-destructive JS-based socket wake-up after 45s of outbox pending state.
- Completed full release protocol (updated `VERSION`, `CHANGELOG.md`, `README.md`, `STATE.md`, `JOURNAL.md`).
- Validated with unit test suite (`pytest` 3/3 passed) and dry-run.

## In-Progress Work
- Ready to commit, tag, and push `v1.1.28` to GitHub `origin/master`.

## Blockers
- None.

## Context Dump

### Decisions Made
- `DEC-030`: Outbox pending state (`🕒`) on slow e2-micro VMs must NOT trigger page reloads, as reloading the page destroys active WebSockets and triggers HTTP 410 errors. Instead, poll for up to 300s to allow normal network flush.
- `DEC-031`: Mandatory release protocol checklist strictly requires updating `README.md` version banner alongside `VERSION` and `CHANGELOG.md`.
- `DEC-032`: Service Worker caches (`CacheStorage`, `ScriptCache`) must NEVER be deleted in `clean_browser_bloat()`, and `--disable-background-networking` must not be used, as both break WhatsApp Web's WebSocket sync engine. Messages with detected outbox clock icons must NEVER trigger `SOFT SUCCESS`.

### Files of Interest
- `broadcaster.py`: Broadcaster engine logic with sticky outbox detection & socket health checks (v1.1.28).
- `browser_config.py`: Hardened Chrome launch config preserving Service Worker caches (v1.1.28).
- `VERSION`: `1.1.28`.
- `README.md`: Updated with `v1.1.28` version banners.
- `CHANGELOG.md`: Full release history.

## Next Steps
1. Push commit and tag `v1.1.28` to GitHub `origin/master`.
2. On the GCP VM, pull the latest code: `git pull origin master`
3. Clear any lingering maintenance/success flags: `rm -f .gsd/last_success.date .gsd/needs_maintenance`
4. Execute the broadcast manually: `bash scripts/run_vm.sh --force`
5. Confirm message delivery in the WhatsApp group.

