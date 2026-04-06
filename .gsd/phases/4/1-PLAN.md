---
phase: 4
plan: 1
wave: 1
---

# Plan 4.1: Headless Test + File Logging

## Objective
Test if headless=True works for production after session is established. Add file logging for unattended monitoring.

## Context
- .gsd/phases/4/RESEARCH.md
- broadcaster.py
- main.py

## Tasks

<task type="auto">
  <name>Test headless=True locally</name>
  <files>broadcaster.py, main.py</files>
  <action>
    1. Add a CLI flag to main.py: `--headless` (default False for dev, True for prod)
    2. Pass headless flag through to run_broadcaster()
    3. Run: `py main.py --headless`
    4. Check if message arrives in WhatsApp group
    5. If fails: document error, keep headless=False as requirement
    6. If works: update DEC-007 to "headless=True works for production"
  </action>
  <verify>Run `py main.py --headless` and confirm message delivered to group</verify>
  <done>Headless mode either confirmed working or confirmed blocked (documented)</done>
</task>

<task type="auto">
  <name>Add file logging</name>
  <files>main.py</files>
  <action>
    1. Add Python logging: dual handler (console + logs/notifier_YYYY-MM-DD.log)
    2. Format: [YYYY-MM-DD HH:MM:SS] LEVEL: message
    3. Create logs/ dir if not exists
    4. Add logs/ to .gitignore
  </action>
  <verify>Run main.py, check logs/ contains today's log file with output</verify>
  <done>Log file created with timestamped entries</done>
</task>

## Success Criteria
- [ ] headless=True tested and result documented
- [ ] File logging active in logs/ directory
- [ ] logs/ in .gitignore
