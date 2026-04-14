# STATE.md - Project Memory

> **Current Phase**: Phase 5 - Live Support & Stability
> **Last Update**: 2026-04-14 10:03 COT
> **Status**: Active — Sprint 2 code complete, awaiting VM deployment

## Current Position
- **Phase**: Phase 5 - Live Support & Stability
- **Sprint**: Sprint 2 - delivery-reliability (code complete)
- **Task**: Deploy to VM + verify next CRON run
- **Status**: Active (resumed 2026-04-14 09:00 COT)

## Last Session Summary
Diagnosed second consecutive CRON failure (2026-04-14 12:00 UTC). New failure mode:
- press_sequentially timed out at 30s (BUG-004) on the e2-micro
- Error handler's page.screenshot() also timed out (BUG-003), crashing the process
- Connectivity banner still present from yesterday (BUG-001 confirmed recurring)

All 4 bugs fixed and pushed in single commit (cd015fc):
- BUG-001: connectivity_guard() with 60s polling before send loop
- BUG-002: main.py exits 1 on failure (no more "Task completed successfully!" lies)
- BUG-003: safe_screenshot() wrapper with try/except at all 5 call sites
- BUG-004: press_sequentially timeout → 60s, wait_for → 60s

Tag v1.0.2 updated to point at cd015fc.

## In-Progress Work
- VM deployment pending: `git pull` on VM needed
- Next CRON run: 2026-04-15 12:00 UTC (7:00 AM COT)

## Blockers
- None. Code is on GitHub, ready for VM pull.

## Context Dump

### Decisions Made
- **DEC-021 (Locators over Handles)**: Self-healing Locators for React re-renders on slow hardware.
- **Phase 5 Sprint Model**: Post-deployment hardening managed in time-boxed sprints.
- **Tag naming**: v{major}.{minor}.{patch} only — pre-release is a GitHub UI toggle.
- **Bug traceability**: Every fix must link BUG-NNN ID in both BUGS.md and CHANGELOG.md.
- **Safe screenshots**: Diagnostic screenshots are best-effort, never crash-inducing.
- **Exit code contract**: run_broadcaster() returns bool; main.py converts to exit code.

### All Bugs Fixed in v1.0.2
- **BUG-001**: connectivity_guard() polls for "Retrying" banner, aborts if >60s
- **BUG-002**: main.py catches RuntimeError + checks bool return → sys.exit(1)
- **BUG-003**: safe_screenshot() wrapper, 10s timeout, try/except
- **BUG-004**: press_sequentially timeout=60000, wait_for timeout=60000

### Files Changed in Sprint 2
- broadcaster.py (BUG-001, BUG-003, BUG-004 + return value)
- main.py (BUG-002: exit code propagation)
- .gsd/phases/5/BUGS.md (all 4 bugs documented and marked fixed)
- .gsd/phases/5/1-PLAN.md (BUG-3 and BUG-4 task blocks added)
- CHANGELOG.md (BUG-003 and BUG-004 entries added)
- .gsd/SPRINT.md (tasks updated, Day 2 log added)

## Next Steps
1. Deploy to VM: SSH → `cd wa_trm_notifier && git pull`
2. Optional: manual test run on VM (`./scripts/run_vm.sh`)
3. Wait for CRON run 2026-04-15 12:00 UTC
4. Fetch logs → if passing: close Sprint 2, promote v1.0.2 to stable
5. If failing: diagnose new issue, open Sprint 3
