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

## Must-Haves
- [ ] WA "Retrying" banner detected before send — abort cleanly if timed out
- [ ] main.py exits non-zero on broadcaster failure
- [ ] Local dry-run confirmed both fixes work independently

## Success Criteria
- [ ] All tasks verified passing
- [ ] Deployed to VM
- [ ] Next autonomous CRON run exits 0 on success, 1 on failure (confirmed via logs)
