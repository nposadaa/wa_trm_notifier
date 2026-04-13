# Sprint 2 — delivery-reliability

> **Duration**: 2026-04-14 to 2026-04-16
> **Status**: In Progress

## Goal
Fix BUG-1 (connectivity guard) and BUG-2 (exit code propagation) before the next CRON run so delivery failures are detected and reported correctly.

## Scope

### Included
- Pre-send connectivity guard (`broadcaster.py`)
- Exit code propagation to `main.py`
- Local dry-run verification + VM deployment

### Explicitly Excluded
- Multi-recipient support
- Session refresh / re-auth automation
- Phase 4 documentation cleanup

## Tasks

| Task | Assignee | Status | Est. Hours |
|------|----------|--------|------------|
| BUG-1: Connectivity guard in broadcaster.py | Claude | ⬜ Todo | 1.0 |
| BUG-2: Exit code propagation in main.py | Claude | ⬜ Todo | 0.5 |
| Local dry-run verification | Claude | ⬜ Todo | 0.5 |
| Deploy to VM + confirm next CRON | Claude | ⬜ Todo | 0.5 |

## Daily Log

### Day 1 (2026-04-14)
- Sprint created from post-mortem of first autonomous CRON failure (2026-04-13)
- Root cause confirmed via diag_delivery_failed_COP_USD Notifier.png
- Phase 5 plan documented in .gsd/phases/5/1-PLAN.md

## Risks & Blockers

| Risk | Impact | Mitigation |
|------|--------|------------|
| Connectivity guard too aggressive (blocks send on transient glitch) | Med | Use 60s timeout before aborting, not instant fail |
| sys.exit(1) in main.py breaks interactive/local use | Med | Only call in broadcaster failure path; document in DECISIONS.md |

## Retrospective (end of sprint)

### What Went Well
-

### What Could Improve
-

### Action Items
- [ ]

---

*Last updated: 2026-04-13*
