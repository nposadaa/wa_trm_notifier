# STATE.md - Project Memory

> **Current Milestone**: v1.3.1 — Hotfix: Spanish Accent Verification & Scoping ✅ Released (2026-10-23)
> **Last Completed Milestone**: v1.3.0 — Dual Broadcast (2026-10-22)
- **Status**: Released — tag `v1.3.1` tagged and ready for VM pull

## Current Position
- **Milestone**: v1.3.1 — Hotfix: Spanish Accent Verification & Scoping ✅ Complete
- **Status**: Released (2026-10-23 14:10 COT)
- **Test Suite**: 28/28 passing

## Last Session Summary
1. Diagnosed first closing broadcast failure at 1:15 PM COT: `Máximo` accent was stripped by legacy non-ASCII regex, causing false-positive verification crash and `UnboundLocalError`.
2. Implemented `normalize_message_text()` and `extract_message_snippet()` in `broadcaster.py`: preserves Spanish accents (`á`, `é`, `í`, `ó`, `ú`, `ñ`), strips emojis, normalizes unicode (NFC), collapses whitespace.
3. Scoped verification variables in outer scope to permanently eliminate `UnboundLocalError`.
4. Replaced single-shot crash on new row with resilient 30-second DOM polling loop.
5. Added 3 unit tests in `tests/test_broadcaster_recovery.py` (28/28 passing).
6. Confirmed live morning and closing dry-runs.

## In-Progress Work
- Fix committed: `280f47d`.
- Pending push to origin and `git pull` on GCP VM.
- Test status: 28/28 passing.

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
1. ⚠️  Refresh GCP VM `whatsapp_session` if outbox clock issues persist (pending from 2026-10-09).
2. Update VM crontab to dual-broadcast schedule (see `docs/CRON_SETUP.md` §2).
3. Run `/complete-milestone` to archive v1.3.0 and plan v1.4.0.
