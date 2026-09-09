# STATE.md - Project Memory

> **Current Milestone**: v1.1.0 — Financial Intelligence
> **Current Phase**: Phase 5 — Live Support & Stability (Hotfixes)
- **Sprint**: Hotfix: Service Worker Preservation & Auth Loop Recovery (v1.1.30)
- **Status**: Paused at 2026-09-09 09:37 COT

## Current Position
- **Phase**: Phase 5 — Live Support & Stability (Hotfixes)
- **Task**: Post-Deployment Observation of v1.1.30
- **Status**: Paused at 2026-09-09 09:37 COT

## Last Session Summary
- Fetched remote GCP logs and diagnosed 4+ day broadcast failure loop (Sep 2 – Sep 9).
- Identified root cause: `deep_clean_profile()` deleted `./whatsapp_session/Default/Service Worker` on maintenance flags, corrupting WhatsApp Web's database and causing Chrome page crashes during authentication.
- Released `v1.1.30`:
  - Updated `deep_clean_profile()` in `browser_config.py` to preserve `Service Worker` and `IndexedDB` sync directories (DEC-034).
  - Added unit test `test_deep_clean_preserves_service_worker` to `tests/test_broadcaster_recovery.py` (7/7 tests passing).
  - Completed release protocol (`VERSION`, `CHANGELOG.md`, `README.md`, `STATE.md`, `JOURNAL.md`, tag `v1.1.30`).
- User executed Zip & Ship protocol locally to deploy a fresh authenticated session zip to the GCP VM.
- VM manual broadcast execution succeeded.

## In-Progress Work
- None (working directory clean, v1.1.30 deployed to GCP VM).
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
1. Observe tomorrow morning's automated CRON run on the GCP VM (12:00 UTC / 7:00 AM COT).
2. Fetch logs with `.\scripts\fetch-logs.ps1` to confirm delivery success and outbox status.
3. Resume roadmap work for Phase 6 (Friday Weekly Summary Message feature).


