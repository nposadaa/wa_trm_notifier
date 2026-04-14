---
phase: 5
plan: 1
wave: 1
---

# Plan 5.1: Delivery Reliability Hardening

## Objective
Fix two root-cause bugs identified from the 2026-04-13 CRON failure post-mortem.
The broadcaster sent a message while WhatsApp Web was in a "Connecting/Retrying" state,
causing the message to be held in outbox (never delivered). Additionally, main.py exits 0
even when the broadcaster reports a delivery failure, making CRON and logs report false success.

## Context
- logs/notifier_2026-04-13.log
- logs/vm_run.log
- broadcaster.py
- main.py

## Tasks

<task type="auto">
  <name>BUG-1: Pre-send connectivity guard</name>
  <files>broadcaster.py</files>
  <action>
    Before typing the message to any recipient, check for the "Connecting to WhatsApp"
    / "Retrying" banner in the sidebar. If detected, wait with exponential backoff
    (up to ~60s) for it to clear. If it does not clear, raise an explicit error and
    abort without sending (do not leave message in outbox).

    Steps:
    1. Locate the banner selector (currently used in banner-clearing logic)
    2. After session stabilization and before the per-recipient send loop, add a
       connectivity_guard() check
    3. Poll every 5s for up to 60s; if still "Retrying" after timeout, raise RuntimeError
    4. Log clearly: "[CONNECTIVITY] Banner clear / [CONNECTIVITY] Timed out - aborting send"

    AVOID: Catching the error silently and proceeding anyway
    USE: A hard abort that bubbles up to main.py
  </action>
  <verify>
    Simulate by artificially cutting network or checking banner text in a test run.
    Confirm log line "[CONNECTIVITY] Timed out" appears and no message is sent.
  </verify>
  <done>
    Broadcaster aborts cleanly (with logged error) when WA is in "Retrying" state.
    No outbox-stuck messages.
  </done>
</task>

<task type="auto">
  <name>BUG-2: Exit code propagation to main.py</name>
  <files>broadcaster.py, main.py</files>
  <action>
    Ensure broadcaster.py communicates failure to main.py so cron sees a non-zero exit.

    Steps:
    1. Audit how broadcaster.py currently signals failure (return value, exception, sys.exit?)
    2. Ensure run_broadcaster() returns a boolean or raises on failure
    3. In main.py: if broadcaster returns failure, call sys.exit(1)
    4. Verify this does NOT break the local interactive workflow (check Architectural
       Consciousness Clause in PROJECT_RULES.md)

    AVOID: Hard sys.exit(1) inside broadcaster.py itself (breaks library-style usage)
    USE: Return value / exception that main.py converts to exit code
  </action>
  <verify>
    Manually trigger a failure (e.g., wrong chat name), run main.py, then:
    `echo $LASTEXITCODE` (PS) should print 1, not 0.
  </verify>
  <done>
    main.py exits 1 on any broadcaster delivery failure. CRON log captures the error.
    "Task completed successfully!" only appears on genuine success.
  </done>
</task>

<task type="auto">
  <name>BUG-3: Safe diagnostic screenshots</name>
  <files>broadcaster.py</files>
  <action>
    All page.screenshot() calls in error handling paths crash the process when the browser
    is frozen, because the screenshot itself times out as an unhandled exception.

    Steps:
    1. Create safe_screenshot(page, path, timeout_ms=10000) wrapper function
    2. Wrap screenshot in try/except — log warning on failure instead of crashing
    3. Replace all 5 raw page.screenshot() call sites with safe_screenshot()

    AVOID: Letting any screenshot call propagate an exception
    USE: Graceful degradation — diagnostic is best-effort, not critical
  </action>
  <verify>
    Confirm no raw page.screenshot() calls remain outside safe_screenshot().
    Simulate frozen browser — process should log warning and continue.
  </verify>
  <done>
    All screenshot calls wrapped. Error handler paths cannot crash the process.
  </done>
</task>

<task type="auto">
  <name>BUG-4: Increase press_sequentially timeout for e2-micro</name>
  <files>broadcaster.py</files>
  <action>
    The default 30s timeout on press_sequentially is too short for the e2-micro VM
    under load. The locator resolves correctly but the typing itself stalls.

    Steps:
    1. Add timeout=60000 to chat_input.press_sequentially() call
    2. Increase chat_input.wait_for() timeout from 45s to 60s for consistency

    AVOID: Setting unreasonably high timeouts (>120s) that mask real failures
    USE: 60s — enough for slow VM, fast enough to fail within CRON window
  </action>
  <verify>
    Confirm press_sequentially call uses timeout=60000.
    Confirm wait_for uses timeout=60000.
  </verify>
  <done>
    Typing timeout doubled from 30s to 60s. wait_for increased from 45s to 60s.
  </done>
</task>

## Must-Haves
- [x] WA "Retrying" banner detected before send — abort cleanly if timed out
- [x] main.py exits non-zero on broadcaster failure
- [x] All screenshot calls wrapped in safe_screenshot() (no crash on frozen browser)
- [x] press_sequentially timeout increased for e2-micro stability
- [x] Local dry-run confirmed all fixes compile cleanly

## Success Criteria
- [x] All tasks verified passing
- [ ] Deployed to VM
- [ ] Next autonomous CRON run exits 0 on success, 1 on failure (confirmed via logs)
