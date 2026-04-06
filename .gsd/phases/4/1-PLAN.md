---
phase: 4
plan: 1
wave: 1
---

# Plan 4.1: Wrapper Script + File Logging

## Objective
Create a batch wrapper that activates the venv and runs main.py, plus add file-based logging so unattended runs can be monitored.

## Context
- main.py
- broadcaster.py
- .gsd/phases/4/RESEARCH.md

## Tasks

<task type="auto">
  <name>Create run_notifier.bat</name>
  <files>run_notifier.bat</files>
  <action>
    Create a Windows batch script at project root that:
    1. cd to the project directory using absolute path
    2. Activates the Python venv
    3. Runs `python main.py`
    4. Appends stdout/stderr to `logs/notifier.log` with timestamp
    5. Creates `logs/` directory if missing
  </action>
  <verify>run_notifier.bat exists and contains valid batch commands; run it once manually</verify>
  <done>Batch file runs main.py successfully when double-clicked or called from cmd</done>
</task>

<task type="auto">
  <name>Add file logging to main.py</name>
  <files>main.py</files>
  <action>
    Add Python logging that writes to both console AND `logs/notifier_YYYY-MM-DD.log`.
    - Use Python logging module with dual handlers (StreamHandler + FileHandler)
    - Log format: `[YYYY-MM-DD HH:MM:SS] LEVEL: message`
    - Create logs/ dir if not exists
    - Add logs/ to .gitignore
  </action>
  <verify>Run main.py and check that logs/notifier_YYYY-MM-DD.log was created with output</verify>
  <done>Log file created with timestamped entries matching console output</done>
</task>

## Success Criteria
- [ ] run_notifier.bat executes pipeline end-to-end
- [ ] Log file created in logs/ with timestamped output
- [ ] logs/ directory in .gitignore
