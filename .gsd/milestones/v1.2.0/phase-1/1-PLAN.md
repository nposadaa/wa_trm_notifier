---
phase: 1
plan: 1
wave: 1
---

# Plan 1.1: Weekday CRON Scheduling

## Objective
Update the schedule to exclude weekends (saving VM resources) by modifying documentation and providing instructions for the user to apply the change on the GCP VM.

## Context
- .gsd/ROADMAP.md
- docs/CRON_SETUP.md

## Tasks

<task type="auto">
  <name>Update CRON_SETUP.md</name>
  <files>docs/CRON_SETUP.md</files>
  <action>
    Update the CRON expression in section 2 from `0 12 * * *` to `0 12 * * 1-5`.
    Add a brief explanation that `1-5` corresponds to Monday through Friday.
  </action>
  <verify>Get-Content docs/CRON_SETUP.md | Select-String "1-5"</verify>
  <done>The CRON expression is documented as weekday-only.</done>
</task>

<task type="checkpoint:human-verify">
  <name>Apply CRON on GCP VM</name>
  <files></files>
  <action>
    Instruct the user to SSH into their GCP VM and run `crontab -e`.
    They must change their schedule from:
    `0 12 * * * cd /home/nposadaa111/wa_trm_notifier && bash scripts/run_vm.sh`
    to:
    `0 12 * * 1-5 cd /home/nposadaa111/wa_trm_notifier && bash scripts/run_vm.sh`
  </action>
  <verify>Ask the user to confirm they have updated the VM crontab.</verify>
  <done>User confirms the VM is updated.</done>
</task>

## Success Criteria
- [ ] `docs/CRON_SETUP.md` reflects the new 1-5 schedule.
- [ ] User confirms the GCP VM crontab is updated.
