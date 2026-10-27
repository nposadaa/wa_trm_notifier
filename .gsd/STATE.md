# STATE.md - Project Memory

> **Current Milestone**: v1.3.2 — WhatsApp Outbox Diagnostics ✅ Released (2026-10-27)
> **Last Completed Milestone**: v1.3.1 — Hotfix: Spanish Accent Verification & Scoping (2026-10-23)
- **Status**: Released — tag `v1.3.2` published to GitHub; VM deployment pending

## Current Position
- **Milestone**: v1.3.2 — WhatsApp Outbox Diagnostics ✅ Complete
- **Status**: Released (2026-10-27)
- **Test Suite**: 32/32 passing

## Last Session Summary
1. Analyzed Oct 26 morning and closing, and Oct 27 morning runs; all showed an outgoing message stuck pending in the WhatsApp outbox.
2. Found the same symptom in weekday logs dating back to Oct 1; the Oct 27 HTTP 400 lacked a URL, so its request could not be identified.
3. Added privacy-safe HTTP/request-failure logs and WhatsApp WebSocket lifecycle diagnostics; clarified that `navigator.onLine` is not proof of WhatsApp connectivity or delivery.
4. Persistent unacknowledged outbox failures now request existing profile maintenance on the next run; explicit WhatsApp send-failure status does not.
5. Updated the runbook and added diagnostic/recovery tests; full suite passes 32/32.

## In-Progress Work
- Diagnostics are included in the published `v1.3.2` release.
- GCP VM pull/deployment remains pending; no VM changes were made as part of this release.
- Test status: 32/32 passing.

## Non-Negotiable Guardrails
- **Friday Weekly Summary Non-Regression**: Weekly TRM intelligence summary (High/Low/Variation) must remain functional in morning edition and all 7 tests in `tests/test_friday_summary.py` must pass at every stage.

## Blockers
- None. VM session refresh recommended before next broadcast.

## Context Dump

### Decisions Made
- Use SET-ICAP official delay API (`proxy.icap.com.co`) for spot market close data instead of fragile HTML scrapers.
- Use explicit `--edition morning` and `--edition closing` flags in `main.py` rather than implicit time-of-day guesses, while keeping a backward-compatible default.
- Separate state deduplication files: `.gsd/last_success_morning.date` and `.gsd/last_success_closing.date` so morning and closing runs do not block each other.

### Files of Interest
- `scraper.py`: Has `scrape_trm()` and `scrape_spot_market()`.
- `main.py`: Target for Phase 2 refactor (CLI flags, deduplication split, closing message template).
- `tests/test_spot_scraper.py`: 7 spot scraper unit tests.
- `tests/test_friday_summary.py`: 7 Friday intelligence unit tests (must not regress).
- `scripts/run_vm.sh` & `docs/CRON_SETUP.md`: Targets for Phase 3 VM deployment and dual cron configuration.

## Next Steps
1. Before deployment or any manual retry, check recipient chats for messages still pending in the outbox to avoid a later duplicate.
2. Pull the `v1.3.2` release on the GCP VM and review the next run's network and delivery-diagnosis logs.
3. If outbox failures persist after the next-run profile maintenance, inspect the new diagnostics before refreshing the WhatsApp session.
