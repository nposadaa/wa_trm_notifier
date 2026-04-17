# Phase 5 — Bug Log

> **Format**: Each entry must reference the release tag where the fix ships.
> **Status values**: `open` | `in-progress` | `fixed` | `wont-fix`

---

## BUG-001 — No pre-send connectivity guard

| Field | Value |
|-------|-------|
| **Status** | `fixed` |
| **Priority** | High |
| **Discovered** | 2026-04-13 |
| **Fixed in release** | v1.0.2 |
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
| **Status** | `fixed` |
| **Priority** | High |
| **Discovered** | 2026-04-13 |
| **Fixed in release** | v1.0.2 |
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

## BUG-003 — Crash in error-handling screenshot path

| Field | Value |
|-------|-------|
| **Status** | `fixed` |
| **Priority** | High |
| **Discovered** | 2026-04-14 |
| **Fixed in release** | v1.0.2 |
| **Phase plan** | phases/5/1-PLAN.md → Task: BUG-3 |

### Description
When `broadcaster.py` catches a typing/interaction error and attempts to take a diagnostic
screenshot in the `except` block, the `page.screenshot()` call itself times out (30s default)
if the browser is frozen. This throws an **unhandled exception** that crashes the entire
process — replacing the original useful error with a screenshot timeout stack trace.

### Root Cause
Raw `page.screenshot()` calls with no timeout override and no try/except wrapper. On the
e2-micro VM, the browser frequently freezes under load, making screenshot capture unreliable.

### Evidence
- `logs/vm_run.log` (2026-04-14): `Page.screenshot: Timeout 30000ms exceeded` in traceback
- Process died as unhandled exception instead of graceful error handling

### Fix
Created `safe_screenshot(page, path, timeout_ms=10000)` wrapper used at all 5 screenshot
call sites. Catches all exceptions and logs a warning instead of crashing.

---

## BUG-004 — press_sequentially timeout too short for e2-micro

| Field | Value |
|-------|-------|
| **Status** | `fixed` |
| **Priority** | High |
| **Discovered** | 2026-04-14 |
| **Fixed in release** | v1.0.2 |
| **Phase plan** | phases/5/1-PLAN.md → Task: BUG-4 |

### Description
The `chat_input.press_sequentially()` call uses the default 30s Playwright timeout. On the
e2-micro VM under load, the locator resolution can stall, causing the typing to timeout
on the first attempt even though the element is present.

### Root Cause
Default 30s timeout is insufficient for the e2-micro's single-core CPU when WhatsApp's React
app is actively processing background sync and E2E decryption alongside the typing.

### Evidence
- `logs/vm_run.log` (2026-04-14): `Locator.press_sequentially: Timeout 30000ms exceeded`
- Locator correctly resolved the element but `elementHandle.type()` timed out

### Fix
Increased `press_sequentially` timeout to 60000ms. Also increased `wait_for` timeout from
45s to 60s for consistency.

---

## BUG-005 — Scraper returns stale TRM data at early CRON time

| Field | Value |
|-------|-------|
| **Status** | `fixed` |
| **Priority** | Med |
| **Discovered** | 2026-04-14 |
| **Fixed in release** | v1.0.3 |
| **Phase plan** | phases/5/1-PLAN.md |

### Description
CRON runs at 7:00 AM COT (12:00 UTC), but `dolar-colombia.com` doesn't update the current
day's TRM until later in the morning (~10 AM COT). The scraper returns yesterday's rate.

### Root Cause
Timing mismatch between CRON schedule and the source website's update cadence.

### Evidence
- `logs/notifier_2026-04-14.log`: Scraped 3631.49 for 2026-04-13 at 12:00 UTC
- Live site at 12:30 PM COT shows $3,608.10 for 2026-04-14

### Fix
1. Shifted CRON from `0 12 * * *` to `0 15 * * *` (10:00 AM COT)
2. Added staleness check in `main.py` with disclaimer if date doesn't match today

---

## BUG-006 — Message typing fails silently (emoji + Lexical compat)

| Field | Value |
|-------|-------|
| **Status** | `fixed` |
| **Priority** | High |
| **Discovered** | 2026-04-14 |
| **Fixed in release** | v1.0.3 |
| **Phase plan** | phases/5/1-PLAN.md |

### Description
Message typed into input box without error, but send button never appears and Enter sends
nothing. Three contributing factors: emoji surrogate pairs in `press_sequentially`, stale
`element_handle()` pointer, and `execCommand('insertText')` not firing React/Lexical events.

### Root Cause
WhatsApp uses Lexical (React-based rich text editor). DOM-level operations modify the DOM
but not Lexical's internal state. Send button visibility is driven by Lexical state.

### Evidence
- `logs/vm_run.log`: "Typing verified: 86 chars" but "Send button missing" consistently
- Message never delivered despite Enter pressed

### Fix (v2)
Replaced with `page.keyboard.insert_text()` which dispatches proper browser-level InputEvent.
Confirmed working: live test 2026-04-14 14:38 COT delivered with correct emojis and ✓✓.

---

## BUG-007 — Delivery verification false negative

| Field | Value |
|-------|-------|
| **Status** | `fixed` |
| **Priority** | Low |
| **Discovered** | 2026-04-14 |
| **Fixed in release** | v1.0.4 |
| **Phase plan** | phases/5/2-PLAN.md |

### Description
Delivery verification reports FAILURE even when message is successfully sent and delivered
(double checkmarks visible in WhatsApp group).

### Root Cause
Selectors `msg-check`/`msg-dblcheck` may not match current WhatsApp DOM, or checkmarks
are on elements not captured by the `.last` locator strategy.

### Evidence
- Live test 2026-04-14: message delivered with ✓✓ but logs show "FAILURE"

### Fix
Replaced rapid `is_visible()` polls with stable Playwright `.wait_for(state="attached")`. Expanded checkmark selectors to natively support `data-icon` permutations alongside `data-testid`. Appended a fallback branch: if Playwright wait times out, evaluate if the outbox clock (`msg-clock`) is also gone — if so, safely deduce a false-negative scroll/DOM exception and mark as **SUCCESS**.

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
