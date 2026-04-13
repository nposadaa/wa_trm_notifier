# Sprint 1 — Delivery Reliability Hardening

> **Phase**: Phase 5 — Live Support & Stability
> **Duration**: 2026-04-14 to 2026-04-16 (3 days)
> **Status**: Planned (not yet started)

## Goal

Eliminate the two root causes of today's silent delivery failure: a missing connectivity guard and a broken exit code pipeline.

---

## Context

Today's CRON run (2026-04-13) failed to deliver despite `main.py` reporting `Task completed successfully!`. Root cause analysis from `vm_run.log` and `diag_delivery_failed_COP_USD Notifier.png` identified two discrete bugs:

1. WhatsApp Web was in **"Connecting to WhatsApp — Retrying"** state at the moment of send. The broadcaster typed the message and pressed Enter, but the WebSocket was down — message was held in outbox (clock icon, never delivered).
2. `main.py` receives a failure signal from `broadcaster.py` but exits with code 0, making CRON and the notifier log report false success.

---

## Scope

### Included
- **BUG-1**: Pre-send connectivity guard in `broadcaster.py`
  - Detect the "Connecting/Retrying" banner before attempting to type the message
  - If banner is present, wait with backoff (up to N seconds) or abort with a clear error
- **BUG-2**: Exit code propagation in `main.py`
  - `broadcaster.py` already saves `diag_delivery_failed.png` — it knows it failed
  - `main.py` must catch this and `sys.exit(1)` so cron logs it correctly
- **Verification**: Confirm fix by reviewing logs and running a local dry-run

### Explicitly Excluded
- Multi-recipient support
- Session refresh / re-auth automation
- Any UI or dashboard changes
- Phase 4 documentation cleanup (separate concern)

---

## Tasks

| # | Task | File(s) | Status | Est. |
|---|------|---------|--------|------|
| 1 | Audit how `broadcaster.py` signals failure to `main.py` | `broadcaster.py`, `main.py` | ⬜ Todo | 30m |
| 2 | Implement connectivity banner detection + backoff loop | `broadcaster.py` | ⬜ Todo | 1h |
| 3 | Wire broadcaster return value → `main.py` exit code | `main.py` | ⬜ Todo | 30m |
| 4 | Local dry-run validation (verify exit codes + log output) | — | ⬜ Todo | 30m |
| 5 | Deploy to VM + confirm next CRON run | VM via `run_vm.sh` | ⬜ Todo | 30m |

**Total estimate**: ~3 hours of focused work

---

## Verification Criteria

- [ ] Running `broadcaster.py` when WA is in "Retrying" state → exits with error, does NOT send
- [ ] Running `main.py` after a broadcaster failure → `echo $?` / CRON log shows exit code `1`
- [ ] Next autonomous CRON run → `notifier_YYYY-MM-DD.log` shows either confirmed delivery OR a clean, named error (not `Task completed successfully!` on failure)

---

## Daily Log

### 2026-04-13
- Sprint created from post-mortem of first autonomous CRON failure
- Root cause confirmed via `diag_delivery_failed_COP_USD Notifier.png` (outbox clock + "Connecting" banner)
- Both bugs logged in `.gsd/TODO.md`
- Phase 5 added to `ROADMAP.md`
