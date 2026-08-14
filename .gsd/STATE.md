# STATE.md - Project Memory

> **Current Milestone**: v1.1.0 — Financial Intelligence
> **Current Phase**: Phase 5 — Live Support & Stability (Hotfixes)
- **Sprint**: Hotfix: Checkmark-Verified Deduplication Guard (v1.1.25)
- **Status**: Release Complete (2026-08-14T10:30:00-05:00)

## Current Position
- **Phase**: Phase 5 — Live Support & Stability (Hotfixes)
- **Task**: Checkmark-Verified Deduplication Guard (v1.1.25)
- **Status**: Release Complete (2026-08-14T10:30:00-05:00)

## Last Session Summary
- Resumed session to analyze 3-day non-delivery issue (Aug 12, Aug 13, Aug 14).
- Synced remote VM logs (`notifier_2026-08-12.log`, `notifier_2026-08-13.log`, `notifier_2026-08-14.log`, `vm_run.log`) via `fetch-logs.ps1`.
- **Root Cause Identified**: `v1.1.22` introduced `SOFT SUCCESS` (BUG-048), which treats any message matched in the DOM as delivered if the composer is empty after 2 minutes. When WhatsApp Web is slow/disconnected, typed messages sit in the local DOM outbox with a **CLOCK ICON** (`🕒`). `SOFT SUCCESS` misclassified these pending outbox messages as successfully delivered, wrote `.gsd/last_success.date`, exited with code 0 (preventing the 10:00 AM retry), and immediately closed the browser context—killing the background socket queue before the message could leave the outbox.
- **Implemented Hotfix v1.1.23**: Expanded outbox clock locators (`msg-time`, `time`, `[aria-label*="Pending"]`, `[aria-label*="Pendiente"]`), blocked `SOFT SUCCESS` whenever a message is stuck in outbox clock icon state, and marked profile maintenance (`needs_maintenance = True`) on outbox stalls.
- **Implemented Hotfix v1.1.24**: Initialized `needs_maintenance = False` at `run_broadcaster` entry to fix `UnboundLocalError`.
- **Implemented Hotfix v1.1.25**: Updated Deduplication Guard to require visible checkmarks (`msg-check`, `msg-dblcheck`, `Delivered`, etc.) on matching last rows before skipping send. Unconfirmed outbox messages will no longer trigger false-positive deduplication skips.

## In-Progress Work
- None. v1.1.25 release protocol complete and pushed to GitHub `origin/master`.



## Blockers
- None.

## Context Dump

### Current Hypothesis
- Code v1.1.23 strictly prevents false-positive soft success when messages are stuck in local outbox pending state. If a slow session stalls in outbox state, the failure is correctly recorded, setting `needs_maintenance = True` and allowing subsequent fallback runs to clean and retry successfully.

### Files of Interest
- `broadcaster.py`: Broadcaster engine logic & delivery verification (v1.1.23).
- `main.py`: Runner entrypoint & `last_success.date` handling.

## Next Steps
1. Push git tag `v1.1.23` and `master` branch to GitHub `origin/master`.


