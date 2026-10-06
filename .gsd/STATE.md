# STATE.md - Project Memory

> **Current Milestone**: v1.3.0 — Dual Broadcast (Morning TRM & Market Close Spot)
> **Last Completed Milestone**: v1.2.0 — Financial Intelligence (2026-10-06)
- **Status**: Phase 1 planned, ready for execution

## Current Position
- **Milestone**: v1.3.0 — Dual Broadcast
- **Phase**: 1 — SET-FX Spot Market Scraper
- **Task**: Planning complete (Plan 1.1 ready)
- **Status**: Ready for execution
- **Test Suite**: 16/16 passing

## Non-Negotiable Guardrails
- **Friday Weekly Summary Non-Regression**: The weekly TRM intelligence summary added in v1.2.0 (High/Low/Variation) must remain intact and functional in the morning broadcast, and all tests in `tests/test_friday_summary.py` must pass at every stage.

## In-Progress Work
- Ready to execute Plan 1.1 (`scrape_spot_market()` implementation and unit tests).

## Blockers
- None.

## Context Dump

### Architectural Insights & API Discovery
- Verified that SET-ICAP public snapshot endpoint returns real-time / 15-min delayed spot data for `USD/COP` including `Apertura`, `Cierre`, `Promedio`, `Precio mínimo`, `Precio máximo`, and `Monto Acumulado`.
- Dual broadcasts will use `--edition morning` (7:00 AM COT, Superfinanciera TRM + Friday summary) and `--edition closing` (1:15 PM COT, SET-FX Spot Close).
- Deduplication files will be separated to prevent collision: `.gsd/last_success_morning.date` and `.gsd/last_success_closing.date`.

### Files of Interest
- `.gsd/phases/1/1-PLAN.md`: Active Phase 1 execution plan.
- `.gsd/phases/1/RESEARCH.md`: API schema and parsing research.
- `scraper.py`: Target for `scrape_spot_market()`.
- `tests/test_spot_scraper.py`: New unit tests for spot market scraper.
- `tests/test_friday_summary.py`: Existing 7 tests that must not regress.

## Next Steps
1. Run `/execute 1` to execute Phase 1 plan.
