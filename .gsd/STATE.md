# STATE.md - Project Memory

> **Current Milestone**: v1.2.0 — Financial Intelligence Spotlight
> **Current Phase**: Phase 3 — Weekly Intelligence (Friday Summary)
- **Sprint**: Phase 3 Release Finalization
- **Status**: Released (2026-10-01 COT)

## Current Position
- **Phase**: Phase 3 — Weekly Intelligence
- **Task**: Friday Weekly Summary feature finalized and release metadata synced
- **Status**: Complete and ready for deployment

## Last Session Summary
- Finished Phase 3 implementation for weekly TRM aggregation and Friday summary formatting.
- Verified the feature set through the live test suite: `16 passed in 0.75s`.
- Updated the release metadata for **v1.2.0**:
  - Bumped `VERSION` to `1.2.0`.
  - Added release notes in `CHANGELOG.md`.
  - Refreshed the README top banner and version footer with a friendly Friday spotlight.
  - Recorded the release in `.gsd/JOURNAL.md` and refreshed project state.

## In-Progress Work
- None. The Friday Weekly Intelligence release is complete.
- Tests status: Passing (16/16 unit tests passing).

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
- `main.py`: Friday weekly summary trigger and formatted TRM intelligence block.
- `scraper.py`: Weekly TRM aggregation with backward-compatible default behavior.
- `.gsd/phases/3/3-1-PLAN.md`: Weekly TRM Aggregation implementation plan.
- `.gsd/phases/3/3-2-PLAN.md`: Friday Summary Message formatting and trigger logic.
- `VERSION`: `1.2.0`.
- `README.md`: Updated with the new Friday weekly intelligence spotlight.
- `CHANGELOG.md`: Full release history.

## Next Steps
1. Deploy the v1.2.0 release to the GCP VM (`git pull origin master`).
2. Run a production Friday check or manual `--friday` dry run to validate the weekly block in context.
3. Continue to the next backlog milestone or prepare the next feature branch.
