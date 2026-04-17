# STATE.md - Project Memory

> **Current Phase**: Phase 5 - Live Support & Stability
> **Last Update**: 2026-04-14 14:50 COT
> **Status**: Active (resumed 2026-04-17 12:16 COT)

## Current Position
- **Phase**: Phase 5 - Operations (Plan 5.2 complete)
- **Task**: All Socrata API integration and BUG-007 tasks complete
- **Status**: Active (Awaiting VM deployment/cron test)

## Last Session Summary
Executed Plan 5.2 (Data Source Migration & Hardening):
- Refactored `scraper.py` to pull TRM data from SuperFinanciera's official 'Datos Abiertos' Socrata JSON API instead of scraping HTML.
- Updated `main.py` message template to cite `www.superfinanciera.gov.co`.
- Fixed BUG-007 (delivery verification false negative) using robust Playwright wait_for strategies for the checkmark element.

**Confirmed working**: Live test at 14:38 COT delivered correct message ($3,608.10 for Apr 14) with emojis and double checkmarks.

Identified **BUG-007** (delivery verification false negative) for future v1.0.4 release — low priority since delivery itself works.

## Releases
| Version | Commit | Status | Content |
|---------|--------|--------|---------|
| v1.0.0 | — | Stable | Initial release |
| v1.0.1 | — | Stable | UI Janitor, reinforced interaction |
| v1.0.2 | cd015fc | Released | BUG-001→004 (connectivity, exit code, safe screenshots, timeouts) |
| v1.0.3 | 23a7494 | Released | BUG-005→006 (scraper timing, Lexical typing) |
| v1.0.4 | — | Planned | BUG-007 (verification false negative) |

## Blockers
- None. Pipeline is working end-to-end.

## Context Dump

### VM Deployment Details
- SSH user: nposadaa111@trm-notifier (zone: us-central1-a)
- Project path: /home/nposadaa111/wa_trm_notifier
- CRON schedule: `0 15 * * *` (10:00 AM COT)
- Run script: scripts/run_vm.sh (uses xvfb-run + --headless)

### Key Decisions
- **DEC-024**: `keyboard.insert_text()` over `press_sequentially` and `execCommand` for Lexical-compatible typing
- **CRON timing**: 10:00 AM COT ensures dolar-colombia.com has updated
- **BUG-007 deferred**: False-negative verification doesn't affect delivery, fix later

## Next Steps
1. Wait for next CRON run (2026-04-15 10:00 AM COT / 15:00 UTC)
2. Fetch logs → if message delivered: promote v1.0.3 to stable
3. Future: fix BUG-007 in v1.0.4 (low priority)
