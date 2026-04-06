---
phase: 4
plan: 2
wave: 2
dependencies: ["4.1"]
---

# Plan 4.2: Windows Scheduled Task

## Objective
Register a Windows Scheduled Task that runs run_notifier.bat every weekday at 7:00 AM COT.

## Context
- run_notifier.bat (created in Plan 4.1)
- .gsd/phases/4/RESEARCH.md

## Tasks

<task type="auto">
  <name>Register Scheduled Task</name>
  <files>run_notifier.bat</files>
  <action>
    Use PowerShell to create a Windows Scheduled Task:
    - Name: "TRM_Notifier_Daily"
    - Trigger: Daily at 7:00 AM
    - Action: Run run_notifier.bat
    - Condition: Run only when user is logged on (display needed for Playwright)
    - Settings: Allow task to be run on demand, do not stop if runs longer than 3 days
  </action>
  <verify>Get-ScheduledTask -TaskName "TRM_Notifier_Daily" returns the task info</verify>
  <done>Task visible in Task Scheduler, next run time shows 7:00 AM tomorrow</done>
</task>

<task type="auto">
  <name>Update ROADMAP and DECISIONS</name>
  <files>.gsd/ROADMAP.md, .gsd/DECISIONS.md</files>
  <action>
    - Update ROADMAP Phase 4 to reflect Windows Task Scheduler (not GitHub Actions)
    - Add DEC-008: Windows Task Scheduler chosen over GitHub Actions
    - Update README.md with scheduling instructions
  </action>
  <verify>grep "Task Scheduler" .gsd/ROADMAP.md returns match</verify>
  <done>All docs reflect the actual deployment strategy</done>
</task>

## Success Criteria
- [ ] Scheduled task registered and visible in Task Scheduler
- [ ] Task configured for 7:00 AM daily, user-logged-on only
- [ ] ROADMAP, DECISIONS, README updated
