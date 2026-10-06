# STATE.md - Project Memory

> **Current Milestone**: v1.3.0 — Dual Broadcast (Morning TRM & Market Close Spot)
> **Last Completed Milestone**: v1.2.0 — Financial Intelligence (2026-10-06)
- **Status**: Paused at 2026-10-06 13:22 COT (Phase 1 complete, Phase 2 ready to plan)

## Current Position
- **Milestone**: v1.3.0 — Dual Broadcast (Morning TRM & Market Close Spot)
- **Phase**: Phase 1 (SET-FX Spot Market Scraper) completed & verified
- **Task**: Between phases (ready for Phase 2: Dual Edition CLI & Deduplication)
- **Status**: Paused
- **Test Suite**: 23/23 passing

## Last Session Summary
1. Defined milestone **v1.3.0** to introduce dual WhatsApp broadcasts:
   - Morning edition: Official TRM at 7:00 AM COT (with Friday weekly intelligence preserved).
   - Closing edition: Colombian USD/COP spot market close at 1:15 PM COT.
2. Discovered and validated official SET-ICAP public delayed snapshot API (`https://proxy.icap.com.co/api/v1/ws/public/delay/snapshot?market=71`).
3. Created and executed Phase 1 plan:
   - Implemented `scrape_spot_market()` in `scraper.py` with exponential backoff retries, key normalization (handling accented `Precio mínimo`/`máximo`), and derived metric calculations.
   - Verified live spot data extraction from PowerShell terminal.
   - Created comprehensive unit tests in `tests/test_spot_scraper.py` (7 tests).
   - Ran full test suite: 23/23 passing with zero regressions on `tests/test_friday_summary.py`.

## In-Progress Work
- None uncommitted. Working tree is clean.
- Phase 1 verified and committed.
- Test status: 23/23 passing.

## Non-Negotiable Guardrails
- **Friday Weekly Summary Non-Regression**: Weekly TRM intelligence summary (High/Low/Variation) must remain functional in morning edition and all 7 tests in `tests/test_friday_summary.py` must pass at every stage.

## Blockers
- None.

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
1. Run `/resume` to restore context.
2. Run `/plan 2` to generate Phase 2 execution plans (Dual Edition CLI & Deduplication).
3. Execute Phase 2 (`/execute 2`) to wire `main.py` to the spot scraper with `--dry-run` local testing.
4. Plan and execute Phase 3 (`/plan 3` and `/execute 3`) for GCP VM deployment and dual cron setup.
