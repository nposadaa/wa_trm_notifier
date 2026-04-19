# STATE.md - Project Memory

> **Current Phase**: Phase 5 - Operations (Post-Sprint 5)
> **Last Update**: 2026-04-19
> **Status**: v1.0.6 Released (Stability Patch Applied)

## Current Position
- **Phase**: Phase 5 - Operations
- **Task**: Maintenance & Monitoring
- **Status**: Stable

## Last Session Summary
Finalized **v1.0.5** release focusing on delivery hardening:
- **BUG-008**: Anchored delivery verification to the last message row in `#main` to eliminate false-positives from old checkmarks.
- **BUG-009**: Hardened `connectivity_guard` with `data-icon` selectors and added a pre-composition check.
- Updated documentation (CHANGELOG, BUGS, VERSION) and finalized Sprint 5.
- Migrated `scraper.py` away from HTML parsing to directly query the official SuperFinanciera 'Datos Abiertos' Socrata API (`mcec-87by.json`).
- Updated WhatsApp message template to cite `www.superfinanciera.gov.co`.
- Fixed **BUG-007** (delivery verification false negative): Replaced polling loop with `wait_for(state="attached", timeout=180000)` and added `data-icon` permutation checks. Added robust clock-absence fallback.
- Validated via `--headless` local run. Generated `v1.0.4` release tag.

## In-Progress Work
- None. Code pushed to `master`.

## Blockers
- None.

## Context Dump
- **CRON**: User restored the VM crontab schedule back to its earlier slot (7:00 AM COT / 12:00 UTC) because the new source handles staleness organically.
- **Verification fallback**: Playwright successfully handled the message check timeout and accurately inferred delivery success via the Outbox clock check during our final local validation run.

## Next Steps
1. /resume
2. Check `logs/cron.log` to confirm automated success at 7:00 AM COT.
