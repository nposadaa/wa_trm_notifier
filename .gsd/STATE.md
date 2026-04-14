# STATE.md - Project Memory

> **Current Phase**: Phase 5 - Live Support & Stability
> **Last Update**: 2026-04-14 10:12 COT
> **Status**: Paused — Sprint 2 deployed, awaiting CRON verification

## Current Position
- **Phase**: Phase 5 - Live Support & Stability
- **Sprint**: Sprint 2 - delivery-reliability (deployed to VM)
- **Task**: Verify next CRON run
- **Status**: Paused at 2026-04-14 10:12 COT

## Last Session Summary
Resumed from 2026-04-13 pause. Fetched VM logs, diagnosed second CRON failure (2026-04-14).
Discovered two NEW bugs on top of the two known ones:

All 4 bugs fixed, documented, committed (cd015fc), pushed, and deployed to VM:
- BUG-001: connectivity_guard() — polls "Retrying" banner, aborts after 60s
- BUG-002: main.py exits 1 on failure via try/except + bool return
- BUG-003: safe_screenshot() wrapper — prevents error-handler crashes
- BUG-004: press_sequentially timeout 30s → 60s for e2-micro

Tag v1.0.2 updated to cd015fc. VM deployed via `git stash && git pull`.
Sprint 3 (v1.0.3) created as draft placeholder for future fixes.

## In-Progress Work
- No uncommitted code changes
- VM has stashed local changes (broadcaster.py from prior runs — diagnostic artifacts only)
- Sprint 2 final task: verify next CRON run

## Blockers
- None. Waiting for CRON run 2026-04-15 12:00 UTC (7:00 AM COT)

## Context Dump

### Decisions Made
- **DEC-021**: Self-healing Locators for React re-renders
- **Phase 5 Sprint Model**: Post-deployment hardening in time-boxed sprints
- **Tag naming**: v{major}.{minor}.{patch} — pre-release is GitHub UI toggle
- **Bug traceability**: BUG-NNN in BUGS.md + CHANGELOG.md
- **Safe screenshots**: Diagnostic screenshots are best-effort, never crash-inducing
- **Exit code contract**: run_broadcaster() returns bool; main.py converts to exit code
- **Connectivity guard**: 60s total with backoff [5,5,10,10,15,15]

### VM Deployment Details
- SSH user: nposadaa111@trm-notifier (zone: us-central1-a)
- Project path: /home/nposadaa111/wa_trm_notifier
- CRON schedule: 12:00 UTC daily (7:00 AM COT)
- Run script: scripts/run_vm.sh (uses xvfb-run + --headless)

### Active Sprints
- Sprint 2 (delivery-reliability): code complete, deployed, awaiting verification
- Sprint 3 (v1.0.3): DRAFT — placeholder for issues surfaced by next CRON runs

### Files Changed in Sprint 2
- broadcaster.py (BUG-001, BUG-003, BUG-004 + return value)
- main.py (BUG-002: exit code propagation)
- .gsd/phases/5/BUGS.md, 1-PLAN.md, SPRINT.md, CHANGELOG.md

## Next Steps
1. Wait for CRON run 2026-04-15 12:00 UTC — OR run manual test: `gcloud compute ssh nposadaa111@trm-notifier --zone=us-central1-a --command="cd ~/wa_trm_notifier && bash scripts/run_vm.sh"`
2. Fetch logs: `.\scripts\fetch-logs.ps1`
3. If passing: close Sprint 2, promote v1.0.2 to stable on GitHub
4. If failing: diagnose, log bugs in BUGS.md, execute Sprint 3
