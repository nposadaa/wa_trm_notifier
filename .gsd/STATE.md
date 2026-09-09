# STATE.md - Project Memory

> **Current Milestone**: v1.1.0 — Financial Intelligence
> **Current Phase**: Phase 5 — Live Support & Stability (Hotfixes)
- **Sprint**: Hotfix: Service Worker Preservation & Auth Loop Recovery (v1.1.30)
- **Status**: Completed at 2026-09-09 08:58 COT

## Current Position
- **Phase**: Phase 5 — Live Support & Stability (Hotfixes)
- **Task**: VM Broadcast Execution & Verification of v1.1.30
- **Status**: Completed at 2026-09-09 08:58 COT

## Last Session Summary
- Fetched remote GCP logs via `scripts/fetch-logs.ps1` and direct SSH.
- Diagnosed 4+ day broadcast failure timeline (Sep 2 – Sep 9):
  - Sep 2–3: Outbox pending stalls due to WebSocket sync delay.
  - Sep 4–9: `needs_maintenance` flag triggered `deep_clean_profile()`, which deleted `Default/Service Worker`. Deleting `Service Worker` corrupted WhatsApp Web's database engine, causing page crashes during auth loop on every run and re-triggering `needs_maintenance` in an infinite loop.
- Released `v1.1.30`:
  - Updated `deep_clean_profile()` in `browser_config.py` to preserve `Service Worker` and `IndexedDB` sync directories (DEC-034).
  - Added unit test `test_deep_clean_preserves_service_worker` to `tests/test_broadcaster_recovery.py` (7/7 tests passing).
  - Completed full release protocol (updated `VERSION`, `CHANGELOG.md`, `README.md`, `STATE.md`, `JOURNAL.md`).
  - Committed and tagged `v1.1.30`.

## In-Progress Work
- None (working directory clean, v1.1.30 committed and tagged).
- Tests status: Passing (7/7 tests passing).

## Blockers
- None.

## Context Dump

### Decisions Made
- `DEC-030`: Outbox pending state (`🕒`) on slow e2-micro VMs must NOT trigger page reloads, as reloading the page destroys active WebSockets and triggers HTTP 410 errors. Instead, poll for up to 300s to allow normal network flush.
- `DEC-031`: Mandatory release protocol checklist strictly requires updating `README.md` version banner alongside `VERSION` and `CHANGELOG.md`.
- `DEC-032`: Service Worker caches (`CacheStorage`, `ScriptCache`) must NEVER be deleted in `clean_browser_bloat()`, and `--disable-background-networking` must not be used, as both break WhatsApp Web's WebSocket sync engine. Messages with detected outbox clock icons must NEVER trigger `SOFT SUCCESS`.
- `DEC-033`: The TRM scraper must implement automatic retries with exponential backoff (3 attempts, 3s initial backoff, 15s timeout) to absorb transient 502/503 HTTP errors and network spikes from the Superfinanciera `datos.gov.co` Socrata portal, preventing premature failure alerts.
- `DEC-034`: Maintenance deep clean (`deep_clean_profile()`) must NEVER delete `Default/Service Worker` or `IndexedDB`. Purging Service Worker files destroys WhatsApp Web's sync database and causes Chrome page crashes during authentication. Maintenance cleanups must be restricted to ephemeral non-session files (`Session Storage`, `Blob Storage`).

### Files of Interest
- `browser_config.py`: Hardened Chrome launch config strictly preserving Service Worker directories during deep clean (v1.1.30).
- `tests/test_broadcaster_recovery.py`: Unit test suite verifying Service Worker preservation (v1.1.30).
- `VERSION`: `1.1.30`.
- `README.md`: Updated with `v1.1.30` version banners.
- `CHANGELOG.md`: Full release history.

## Next Steps
1. On the GCP VM, pull the latest code: `git pull origin master`
2. Clear any lingering maintenance/success flags: `rm -f .gsd/last_success.date .gsd/needs_maintenance`
3. Execute the broadcast manually: `bash scripts/run_vm.sh --force`
4. Confirm message delivery in the WhatsApp group.


