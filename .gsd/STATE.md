# STATE.md - Project Memory

> **Current Milestone**: v1.3.0 — Dual Broadcast (Morning TRM & Market Close Spot) ✅ Released (2026-10-22)
> **Last Completed Milestone**: v1.2.0 — Financial Intelligence (2026-10-06)
- **Status**: Released — tag `v1.3.0` created, pending push to GitHub and VM deployment

## Current Position
- **Milestone**: v1.3.0 — Dual Broadcast (Morning TRM & Market Close Spot) ✅ Complete
- **Phase**: Phase 3 (VM Scheduling & Verification) completed & verified
- **Task**: All phases complete — milestone ready for production deployment
- **Status**: Active (2026-10-22 COT)
- **Test Suite**: 25/25 passing

## Last Session Summary
1. Executed Phase 3: updated `scripts/run_vm.sh` and `docs/CRON_SETUP.md`.
2. `run_vm.sh`: added edition label to log header; documented `--edition` passthrough.
3. `CRON_SETUP.md`: full rewrite — dual-cron table (morning 12:00 UTC / closing 18:15 UTC), deduplication state file reference, manual execution guide, troubleshooting.
4. Verified 25/25 tests passing.
5. All 3 phases of v1.3.0 complete.

## In-Progress Work
- Working tree clean.
- All phases verified and committed.
- Test status: 25/25 passing.

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
