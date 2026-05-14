# JOURNAL.md - Project Log

## Session: 2026-05-03 18:36 (COT)

### Objective
Establish a backlog and plan the next milestone for the TRM Notifier.

### Accomplished
- ✅ **Resumed Session**: Synchronized context from v1.0.8 stable state.
- ✅ **Created BACKLOG.md**: Defined 4 new features (Trend Emojis, Weekday CRON, Weekly Summary, 5-Year Alerts).
- ✅ **Archived v1.0**: Moved legacy phases and session files to `.gsd/milestones/1/`.
- ✅ **Initialized v1.1.0**: Defined milestone goals and a 4-phase roadmap.
- ✅ **Reset Session Files**: Fresh start for JOURNAL.md and DECISIONS.md.

### Verification
- [x] BACKLOG.md correctly formatted and populated.
- [x] ROADMAP.md reflects new v1.1.0 phases.
- [x] v1.0 history preserved in archive.

### Paused Because
User requested pause after milestone initialization.

### Handoff Notes
We are ready to start **Phase 1: Scheduling & Optimization**. The goal is to update the VM CRON to skip weekends.

---

## Session: 2026-05-03 19:12

### Objective
Execute phase 1 & 2 of the Financial Intelligence milestone and release v1.1.0.

### Accomplished
- ✅ Executed Phase 1: Weekday CRON Scheduling.
- ✅ Executed Phase 2: Comparative Logic and Trend Emojis.
- ✅ Added `--dry-run` to `main.py`.
- ✅ Updated `CHANGELOG.md` and `README.md`.
- ✅ Tagged release `v1.1.0` on git.

### Verification
- [x] Tested Phase 2 logic using `--dry-run`.
- [x] User successfully updated GCP VM crontab.

### Paused Because
User requested to pause after releasing v1.1.0 features.

### Handoff Notes
Next up is Phase 3: Weekly Intelligence (creating a specialized summary message for Fridays).

---

## Session: 2026-05-07 08:36 (COT)

### Objective
Diagnose and fix silent failure of messages not arriving in the WhatsApp group.

### Accomplished
- ✅ Analyzed `vm_run.log` and discovered message was sent to wrong chat due to Text Fallback search matching a previous message.
- ✅ Removed dangerous Text Fallback search logic in `broadcaster.py`.
- ✅ Increased exact match timeout to 8 seconds.
- ✅ Released `v1.1.3` and updated documentation.

### Verification
- [x] Tested search logic locally and pushed to VM.
- [x] VM successfully ran the fix and updated packages.

### Paused Because
Hotfix completed and deployed. Ready for next phase.

### Handoff Notes
Next up is Phase 3: Weekly Intelligence.

---

## Session: 2026-05-04 08:36 (COT)

### Objective
Diagnose and resolve the silent failures of the v1.1.0 TRM Notifier broadcast on the GCP VM.

### Accomplished
- ✅ Diagnosed false-positive delivery logs (anchoring to previous day's message).
- ✅ Fixed React DOM input state sync by injecting 'type(space)'.
- ✅ Fixed Send button locators for WhatsApp Web.
- ✅ Overhauled delivery verification with a 30s DOM polling loop to handle extreme latency on e2-micro VMs.
- ✅ Released and deployed v1.1.1 to the VM.
- ✅ Verified successful run on VM (Message went out).

### Verification
- [x] VM log shows SUCCESS: Delivery Confirmed after 64s wait.
- [x] User physically verified message received in the WhatsApp Group.

### Paused Because
Session handoff requested before starting Phase 3.

### Handoff Notes
Everything is stable. The next phase is Phase 3: Weekly Intelligence.

---

## Session: 2026-05-09 10:40

### Objective
Investigate report of "failed send today again" (May 9th) and evaluate stability of v1.1.3.

### Accomplished
- ✅ **Analyzed Logs**: Confirmed no execution occurred on Saturday (May 9th) due to Weekday-only CRON configuration.
- ✅ **Discovered Friday Skip**: Identified that Friday (May 8th) also failed to generate any logs, suggesting a VM/CRON issue.
- ✅ **Verified v1.1.3**: Local dry-run confirms scraper and formatting logic are correct and functional.
- ✅ **Defined Reversion Strategy**: Outlined a "Safe Revert" path to v1.0.8 while preserving v1.1.3 search hardening.

### Verification
- [x] `main.py --dry-run` successful.
- [ ] Monday execution verification (Pending).

### Paused Because
User decided to wait until Monday to gather more data before deciding on a reversion.

### Handoff Notes
If Monday fails, the priority is to revert to v1.0.8 logic (Daily schedule, no trend emojis) but KEEP the v1.1.3 exact-match search logic to avoid wrong-chat delivery.

---

## Session: 2026-05-11 10:55 (COT)

### Objective
Diagnose the Monday broadcast failure and implement a long-term stability solution.

### Accomplished
- ✅ **Diagnosed Friday Failure**: Confirmed VM was down during the 12:00 UTC window on May 8th.
- ✅ **Diagnosed Monday Timeout**: Found browser hung in `SYNCING...` state on the VM.
- ✅ **Hard Purge**: Deleted browser cache and temporary data on VM to restore performance.
- ✅ **Implemented Resilient Scheduling**: Added a 15:00 UTC (10:00 AM COT) secondary CRON run.
- ✅ **Implemented Success Tracking**: Added `.gsd/last_success.date` to prevent double-posting.
- ✅ **Implemented Failure Notifications**: Added proactive "API Down" alerts for the group.
- ✅ **Verified v1.1.4**: Manual run successfully detected API outage and sent the "API Down" status message to WhatsApp.

### Verification
- [x] Manual run confirmed "API Down" message delivery.
- [x] Crontab on VM successfully updated with dual-run schedule.
- [x] Success file logic prevents redundant runs.

### Paused Because
v1.1.4 release complete and stability features verified.

### Handoff Notes
The system is now self-healing. Tomorrow's run will automatically try at 7:00 AM and retry at 10:00 AM if the API is down or if it crashes. Ready for Phase 3: Weekly Intelligence.

---

## Session: 2026-05-12 12:11 (COT)

### Objective
Diagnose the failure of the 10:00 AM retry and fix the "False Success" verification bug.

### AccomplISHED
- ✅ **Diagnosed False Positive**: Discovered that the broadcaster was matching the May 7th checkmark/text after a recovery reload, leading to a false "Success" report.
- ✅ **Fixed Stale Composer**: Identified that old messages were stuck in the input box; implemented a robust 3-pass clear loop and verification.
- ✅ **Hardened Verification**: Updated `broadcaster.py` to re-verify row text inside the status polling loop.
- ✅ **Added Force Flag**: Implemented `--force` in `main.py` to allow manual retries when the automatic run incorrectly records a success.
- ✅ **Timestamped Screenshots**: Prevented diagnostic confusion by adding timestamps to PNG filenames.

### Verification
- [x] Local dry-run with `--force` successful.
- [x] Scraper verified (returning correct May 12 data).
- [x] Code committed and ready for VM deployment.

### Paused Because
Hotfix v1.1.6 complete. Ready to deploy and run a manual recovery on the VM.

### Handoff Notes
Run `git pull` on the VM followed by `python3 main.py --headless --force` to finally send today's correct data. The system is now significantly more resistant to stale-state false positives.

---

## Session: 2026-05-12 12:38 (COT)

### Objective
Fix the `NameError` crash introduced in v1.1.6.

### AccomplISHED
- ✅ **Hotfix v1.1.7**: Added missing `datetime` import to `broadcaster.py`.
- ✅ **Protocol**: Updated Version, Changelog, and Pushed to remote.

### Verification
- [x] Code verified and pushed.

### Paused Because
Hotfix complete.

### Handoff Notes
Ready for final manual run on VM.
---

## Session: 2026-05-14 18:05 (COT)

### Objective
Diagnose and fix May 14th delivery failure (silent failure on GCP VM).

### Accomplished
- ✅ **Diagnosed Failure**: Confirmed via VM logs that the session was invalidated (`QR Required`).
- ✅ **Zip & Ship**: Guided user through local re-authentication and session transfer.
- ✅ **Identified Maintenance Loop**: Discovered that a stale `.gsd/needs_maintenance` flag was causing the script to delete the `IndexedDB` of the newly transferred session on every run.

### Verification
- [x] `logs/vm_run.log` correctly identified session invalidation.
- [x] `whatsapp_session.zip` successfully transferred and unzipped on VM.
- [ ] Final successful broadcast (Pending removal of maintenance flag).

### Paused Because
User requested pause.

### Handoff Notes
The fix is operational:
1. Run `rm .gsd/needs_maintenance` on the VM.
2. Run `unzip -o whatsapp_session.zip` on the VM to restore the deleted database.
3. Run `bash scripts/run_vm.sh --force`.
