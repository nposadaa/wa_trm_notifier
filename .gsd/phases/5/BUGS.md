# Phase 5 — Bug Log

> **Format**: Each entry must reference the release tag where the fix ships.
> **Status values**: `open` | `in-progress` | `fixed` | `wont-fix`

---

## BUG-001 — No pre-send connectivity guard

| Field | Value |
|-------|-------|
| **Status** | `open` |
| **Priority** | High |
| **Discovered** | 2026-04-13 |
| **Fixed in release** | — |
| **Phase plan** | phases/5/1-PLAN.md → Task: BUG-1 |

### Description
`broadcaster.py` attempts to type and send the message even when WhatsApp Web is in a
"Connecting to WhatsApp — Retrying" state. The message is composed and Enter is pressed,
but the WebSocket is down — the message is held in the outbox (clock icon) and never
delivered to the recipient.

### Root Cause
No connectivity check exists before the per-recipient send loop. The session stabilization
check only validates login state, not ongoing WebSocket health.

### Evidence
- `logs/vm_run.log` (2026-04-13): `"Connecting to WhatsApp — Retrying"` visible in sidebar
- `diag_delivery_failed_COP_USD Notifier.png`: clock icon (⏰) on sent message, no checkmarks
- Browser errors: `"2 FS.syncfs operations in flight"`, `"Failed to load resource: 400"`

### Fix
Add `connectivity_guard()` function in `broadcaster.py` that polls for the "Retrying" banner
before the send loop. Abort with `RuntimeError` if banner persists beyond 60s timeout.

---

## BUG-002 — Broadcaster failure not propagated to main.py exit code

| Field | Value |
|-------|-------|
| **Status** | `open` |
| **Priority** | High |
| **Discovered** | 2026-04-13 |
| **Fixed in release** | — |
| **Phase plan** | phases/5/1-PLAN.md → Task: BUG-2 |

### Description
`main.py` logs `"Task completed successfully!"` and exits with code `0` even when
`broadcaster.py` detects and logs a delivery failure. This causes CRON to report no error,
and the notifier log provides false confidence that the broadcast succeeded.

### Root Cause
`main.py` does not inspect the return value or exception state of the broadcaster call.
The broadcaster saves `diag_delivery_failed.png` and logs a `FAILURE` line but does not
raise an exception or return a falsy value that `main.py` acts on.

### Evidence
- `logs/notifier_2026-04-13.log`: `"[INFO] Task completed successfully!"` immediately after
  broadcaster logged `"FAILURE: Message held in Outbox"`
- CRON exit status: `0` (success) despite no delivery

### Fix
- `broadcaster.py`: raise exception or return `False` on delivery failure (no `sys.exit` inside broadcaster)
- `main.py`: catch failure return/exception and call `sys.exit(1)`
- Document decision in `DECISIONS.md` per Architectural Consciousness Clause

---

## Template for new bugs

Copy this block when logging a new bug:

```markdown
## BUG-NNN — Short title

| Field | Value |
|-------|-------|
| **Status** | `open` |
| **Priority** | High / Med / Low |
| **Discovered** | YYYY-MM-DD |
| **Fixed in release** | — |
| **Phase plan** | phases/5/N-PLAN.md → Task: ... |

### Description
{What went wrong from a user/operator perspective}

### Root Cause
{Technical explanation of why it happens}

### Evidence
{Log lines, screenshots, or commands that prove the bug}

### Fix
{Intended fix approach — brief}
```
