# STATE.md - Project Memory

> **Current Milestone**: v1.3.0 — Dual Broadcast (Morning TRM & Market Close Spot)
> **Last Completed Milestone**: v1.2.0 — Financial Intelligence (2026-10-06)
- **Status**: Phase 1 verified and complete, ready for Phase 2

## Current Position
- **Milestone**: v1.3.0 — Dual Broadcast
- **Phase**: 1 completed, ready for Phase 2
- **Status**: Verified
- **Test Suite**: 23/23 passing

## Last Session Summary
Phase 1 (SET-FX Spot Market Scraper) executed successfully:
- Implemented `scrape_spot_market()` in `scraper.py` extracting official SET-ICAP delayed snapshot metrics (`cierre`, `apertura`, `promedio`, `minimo`, `maximo`, `change`, `change_pct`, `transacciones`, `monto_acumulado`, `fecha`).
- Created unit tests in `tests/test_spot_scraper.py` (7 tests).
- Verified full test suite (23 passing), with zero regression on Friday weekly summary (`test_friday_summary.py` 7/7 passing).
- Live API call verified against `proxy.icap.com.co`.

## Non-Negotiable Guardrails
- **Friday Weekly Summary Non-Regression**: The weekly TRM intelligence summary added in v1.2.0 (High/Low/Variation) must remain intact and functional in the morning broadcast, and all tests in `tests/test_friday_summary.py` must pass at every stage.

## In-Progress Work
- Ready to plan and execute Phase 2: Dual Edition CLI & Deduplication (Zero-Regression).

## Blockers
- None.

## Context Dump

### Architectural Insights & API Discovery
- Verified that SET-ICAP public snapshot endpoint returns real-time / 15-min delayed spot data for `USD/COP` including `Apertura`, `Cierre`, `Promedio`, `Precio mínimo`, `Precio máximo`, and `Monto Acumulado`.
- Dual broadcasts will use `--edition morning` (7:00 AM COT, Superfinanciera TRM + Friday summary) and `--edition closing` (1:15 PM COT, SET-FX Spot Close).
- Deduplication files will be separated to prevent collision: `.gsd/last_success_morning.date` and `.gsd/last_success_closing.date`.

### Files of Interest
- `scraper.py`: Contains `scrape_trm()` and newly added `scrape_spot_market()`.
- `main.py`: Target for Phase 2 `--edition morning|closing` refactor.
- `tests/test_spot_scraper.py`: Spot scraper test suite (7 tests).
- `tests/test_friday_summary.py`: Existing 7 tests guarded against regression.

## Next Steps
1. Run `/plan 2` to create Phase 2 execution plans.
