# ROADMAP.md

> **Current Milestone**: v1.3.0 — Dual Broadcast (Morning TRM & Market Close Spot) ✅ Complete (2026-10-22)
> **Goal**: Enable dual daily WhatsApp broadcasts: morning official TRM (7:00 AM COT) and Colombian market closing spot rate (1:00 PM COT / SET-FX close) with dedicated edition flags, state deduplication, and cron scheduling — with zero regression to Friday weekly intelligence.

## Must-Haves
- [x] **SET-FX Spot Scraper**: Fetch intraday spot indicators (Cierre, Apertura, Promedio, Mínimo, Máximo) from SET-ICAP official API (`proxy.icap.com.co`) with unit tests.
- [x] **Dual Edition CLI & Deduplication**: Support `--edition morning|closing` with independent deduplication guards (`last_success_morning.date` & `last_success_closing.date`) so neither blocks the other.
- [x] **Zero Regression for Friday Weekly Summary**: Ensure the Friday weekly TRM intelligence summary (High/Low/Variation) remains fully operational and tested in the morning edition with all 7 `test_friday_summary.py` tests passing.
- [x] **Closing Message Template**: Format market close message with spot close, intraday spread (Min/Max), and change vs open.
- [x] **Dual Cron VM Configuration**: Update VM runner script and documentation for 7:00 AM COT (12:00 UTC) and 1:15 PM COT (18:15 UTC) scheduling.

## Phases

### Phase 1: SET-FX Spot Market Scraper
**Status**: ✅ Complete
**Objective**: Build and unit-test a robust spot scraper targeting the official SET-ICAP public endpoint (`proxy.icap.com.co`) for USD/COP spot market indicators.

### Phase 2: Dual Edition CLI & Deduplication (Zero-Regression)
**Status**: ✅ Complete (2026-10-22)
**Objective**: Refactor `main.py` with `--edition morning|closing` support, independent deduplication state files, custom message templates for morning vs close, and guaranteed non-regression of the Friday weekly summary.

### Phase 3: Integration, VM Scheduling & Verification
**Status**: ✅ Complete (2026-10-22)
**Objective**: Update `scripts/run_vm.sh`, update `docs/CRON_SETUP.md`, and verify end-to-end functionality via dry-run and full regression test suite.

---

## Milestone Archive

### v1.2.0 — Financial Intelligence
**Status**: ✅ Complete (2026-10-06)
**Objective**: Enhance the notification with trend analysis, historical context, and optimized delivery.
- [x] **Phase 1**: Scheduling & Optimization — weekday-only CRON.
- [x] **Phase 2**: Comparative Logic — trend emoji (📈/📉) with previous day comparison.
- [x] **Phase 3**: Weekly Intelligence — Friday summary with High/Low/Trend.
- Phase 4 (Historical Deep-Dive) — cancelled.

### v1.0 — Daily TRM Broadcast
**Status**: ✅ Complete (v1.0.8 stable)
**Objective**: Automate daily TRM notifications via WhatsApp Playwright on GCP.
- [x] **Phase 1-3**: Local foundation, Meta API pivot to Playwright.
- [x] **Phase 4**: GCP VM Deployment & Xvfb automation.
- [x] **Phase 5**: Stability hardening (Auto-cleanup, emoji-neutral verification).
