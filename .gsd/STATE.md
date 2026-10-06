# STATE.md - Project Memory

> **Current Milestone**: v1.3.0 — Dual Broadcast (Morning TRM & Market Close Spot)
> **Last Completed Milestone**: v1.2.0 — Financial Intelligence (2026-10-06)
- **Status**: Milestone planned, ready for Phase 1

## Current Position
- **Milestone**: v1.3.0 — Dual Broadcast
- **Phase**: Not started
- **Status**: Milestone planned
- **Test Suite**: 16/16 passing

## In-Progress Work
- None. Ready to plan and execute Phase 1 (SET-FX Spot Market Scraper).

## Non-Negotiable Guardrails
- **Friday Weekly Summary Non-Regression**: The weekly TRM intelligence summary added in v1.2.0 (High/Low/Variation) must remain intact and functional in the morning broadcast, and all tests in `tests/test_friday_summary.py` must pass at every stage.

## Blockers
- None. Official SET-ICAP delay API (`proxy.icap.com.co/api/v1/ws/public/delay/snapshot?market=71`) identified and validated.

## Context Dump

### Architectural Insights & API Discovery
- Verified that SET-ICAP public snapshot endpoint returns real-time / 15-min delayed spot data for `USD/COP` including `Apertura`, `Cierre`, `Promedio`, `Precio mínimo`, `Precio máximo`, and `Monto Acumulado`.
- Dual broadcasts will use `--edition morning` (7:00 AM COT, Superfinanciera TRM + Friday summary) and `--edition closing` (1:15 PM COT, SET-FX Spot Close).
- Deduplication files will be separated to prevent collision: `.gsd/last_success_morning.date` and `.gsd/last_success_closing.date`.

### Files of Interest
- `scraper.py`: Will include `scrape_spot_market()` or new scraper function.
- `main.py`: CLI entry point to support `--edition morning|closing`.
- `tests/test_friday_summary.py`: Existing 7 tests that must not regress.
- `scripts/run_vm.sh`: VM runner to pass arguments (e.g. `--edition "$@"`).
- `docs/CRON_SETUP.md`: Crontab instructions for dual schedule.

## Next Steps
1. Run `/plan 1` to create Phase 1 execution plans.
