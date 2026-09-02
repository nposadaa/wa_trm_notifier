# STATE.md - Project Memory

> **Current Milestone**: v1.1.0 — Financial Intelligence
> **Current Phase**: Phase 5 — Live Support & Stability (Hotfixes)
- **Sprint**: Hotfix: Resilient TRM Scraper with Exponential Backoff (v1.1.29)
- **Status**: Paused at 2026-09-02 13:16 COT

## Current Position
- **Phase**: Phase 5 — Live Support & Stability (Hotfixes)
- **Task**: VM Broadcast Execution & Verification of v1.1.29
- **Status**: Paused at 2026-09-02 13:16 COT

## Last Session Summary
- Analyzed VM logs after v1.1.28 deployment. Confirmed VM pulled v1.1.28 and preserved Service Worker caches.
- Diagnosed transient HTTP 503 Service Unavailable error from `datos.gov.co` during the 17:08/17:11 UTC runs:
  - `scraper.py` had no retry mechanism; a single transient 503 immediately triggered `main.py`'s API failure notification path.
  - Verified live API status: `datos.gov.co` is online (HTTP 200 OK), returning today's TRM ($3,184.00 COP).
- Released `v1.1.29`:
  - Added automatic retries with exponential backoff (up to 3 attempts with 3s/6s backoff and 15s timeout) to `scraper.py` (DEC-033).
  - Added unit test suite `tests/test_scraper_retry.py` covering first-try success, 503 recovery, and retry exhaustion (6/6 tests passing).
  - Validated dry-run execution (`main.py --dry-run`).
- Completed full release protocol (updated `VERSION`, `CHANGELOG.md`, `README.md`, `STATE.md`, `JOURNAL.md`).
- Pushed release commit and tag `v1.1.29` to GitHub `origin/master`.

## In-Progress Work
- None (working directory clean, v1.1.29 committed, tagged, and pushed to origin/master).
- Tests status: Passing (6/6 tests passing).

## Blockers
- None.

## Context Dump

### Decisions Made
- `DEC-030`: Outbox pending state (`🕒`) on slow e2-micro VMs must NOT trigger page reloads, as reloading the page destroys active WebSockets and triggers HTTP 410 errors. Instead, poll for up to 300s to allow normal network flush.
- `DEC-031`: Mandatory release protocol checklist strictly requires updating `README.md` version banner alongside `VERSION` and `CHANGELOG.md`.
- `DEC-032`: Service Worker caches (`CacheStorage`, `ScriptCache`) must NEVER be deleted in `clean_browser_bloat()`, and `--disable-background-networking` must not be used, as both break WhatsApp Web's WebSocket sync engine. Messages with detected outbox clock icons must NEVER trigger `SOFT SUCCESS`.
- `DEC-033`: The TRM scraper must implement automatic retries with exponential backoff (3 attempts, 3s initial backoff, 15s timeout) to absorb transient 502/503 HTTP errors and network spikes from the Superfinanciera `datos.gov.co` Socrata portal, preventing premature failure alerts.

### Files of Interest
- `scraper.py`: Hardened scraper with exponential backoff retry loop (v1.1.29).
- `broadcaster.py`: Broadcaster engine logic with sticky outbox detection & socket health checks (v1.1.28).
- `browser_config.py`: Hardened Chrome launch config preserving Service Worker caches (v1.1.28).
- `VERSION`: `1.1.29`.
- `README.md`: Updated with `v1.1.29` version banners.
- `CHANGELOG.md`: Full release history.

## Next Steps
1. On the GCP VM, pull the latest code: `git pull origin master`
2. Clear any lingering maintenance/success flags: `rm -f .gsd/last_success.date .gsd/needs_maintenance`
3. Execute the broadcast manually: `bash scripts/run_vm.sh --force`
4. Confirm message delivery in the WhatsApp group.


