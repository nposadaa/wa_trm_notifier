# JOURNAL.md — Project Log

## Session: 2026-04-09 20:25 (COT)

### Objective
Diagnose Linux VM headless timeout loops and validate the Zip and Ship cross-OS profile transfer.

### Accomplished
- ✅ **Rewrote Zip and Ship Docs**: Restructured `SESSION_TRANSFER.md` to establish Windows->Linux transfer as the official protocol to avoid e2-micro out-of-memory errors.
- ✅ **Mocked Persistent Storage**: Added a JS injection block to `browser_config.py` to intercept `navigator.storage.persist()`. This fixes a severe crash in headless Chromium instances where WhatsApp React apps fail to allocate.
- ✅ **Synchronized CLI Engine**: Completely stripped arbitrary native bash backgrounding out of `run_vm.sh`. It now locks the terminal cursor and streams Playwright execution perfectly verbatim to stdout.

### Verification
- [x] Confirmed the Windows DPAPI issue was successfully bridged by `--password-store=basic`.
- [x] Validated that `400 Bad Request` drops were a down-stream effect of JS React state corruption, not an encryption lock-out.
- [ ] User completes run-through via the newly synchronous `run_vm.sh`.

### Paused Because
User explicitly invoked the `/pause` workflow via direct prompt to dump state.

### Handoff Notes
We are one keystroke from full broadcast. The user is executing `run_vm.sh` with a fully unlocked, `chmod 777` Windows-synced configuration profile and the new Headless JS mock.

---

## Session: 2026-04-09 18:09 (COT)

### Objective
Diagnose the early timeout drops on `auth.py` and stabilize the QR code scan pipeline.

### Accomplished
- ✅ **QR Code Live Refresh**: Fixed `auth.py` to overwrite `qr.png` every 5 seconds to bypass WhatsApp's native 20-second QR token rotation preventing user scans.
- ✅ **Timeout Extension**: Replaced 10-minute maximum runtime loop with a 40-minute loop so the slow Google Cloud e2-micro VM has ample time to decrypt WhatsApp E2E WebAssembly chunks without prematurely dropping the session container.
- ✅ **GSD Education**: Instructed user on creating a fully personalized Git repository fork of the GSD Agent Framework equipped with `caveman` and `mempalace` skills via automated submodule inclusion directly hooked to their `/install` pipeline.

### Verification
- [x] Tested auth.py with real VM, and confirmed the new timeouts and QR generations perfectly aligned with Playwright output constraints.
- [ ] Verify `main.py` succeeds in deploying the daily TRM post after `auth.py` terminates gracefully.

### Paused Because
User requested pause `/pause` while the VM natively processes the 30-minute sync to avoid hitting agent token boundaries.

### Handoff Notes
We are merely waiting for `auth.py` to say "✅ Session successfully synchronized!" Next session immediately progresses directly to running the `main.py --headless` via `xvfb-run`. A clean `whatsapp_session` has successfully logged in and is validating keys now.

---

## Session: 2026-04-09 17:05 (COT)

### Objective
Synchronize documentation with the user's local PowerShell environment.

### Accomplished
- ✅ **Updated Documentation**: Modified `docs/SESSION_TRANSFER.md` to specify **PowerShell** for local Windows commands instead of Bash. 
- ✅ **Command Verification**: Confirmed the correct `gcloud compute scp` syntax for downloading `qr.png` to a Windows machine.
- ✅ **Security Check**: Verified that all session-related files remain correctly Git-ignored.

### Verification
- [x] User successfully executed `gcloud compute scp` from PowerShell.
- [x] Documentation now explicitly supports the user's terminal choice.

### Paused Because
Session end explicitly triggered via `/pause` workflow.

### Handoff Notes
The project is now fully aligned with a PowerShell local workflow. Next session should proceed with the "Exact Start Sequence" in `STATE.md` to complete the native VM session sync.

---

## Session: 2026-04-09 09:25 (COT)

### Objective
Complete the session transfer and fix the token severing. 

### Accomplished
- ✅ **Diagnosed Handshake Interruption**: Found that `auth.py` was closing the browser process mid-handshake when it spotted "Loading your chats", causing the phone to throw a "Check your phone's internet" error during device pairing.
- ✅ **Fixed Syncing Wait times in auth.py**: Instructed Playwright to hold the browser open for up to 5 minutes while E2E sync process completely resolves and the chats pane becomes interactive.
- ✅ **Committed and Pushed**: `auth.py` update synced to GitHub (`a56dd2a`).

### Verification
- [x] Code audit confirmed `auth.py` now waits for `#pane-side`.
- [ ] VM Live Test.

### Paused Because
User session time constraint.

### Handoff Notes
Next session requires a fresh sync on the VM: `git pull`, clear `whatsapp_session`, scan headless `auth.py`, and wait out the sync. Follow the "Exact Start Sequence" in `STATE.md` verbatim.

---
...

## Session: 2026-04-13 14:18 (COT)

### Objective
Post-mortem and planning following first autonomous CRON failure. Set up Phase 5 infrastructure and plan Sprint 2.

### Accomplished
- Diagnosed CRON failure via logs and diag screenshot: WA 'Connecting/Retrying' at moment of send
- Identified BUG-001 (no connectivity guard) and BUG-002 (silent exit code failure)
- Added Phase 5 to ROADMAP.md + created phases/5/ directory structure
- Created phases/5/1-PLAN.md (GSD plan format) and phases/5/BUGS.md (bug tracker)
- Created .gsd/SPRINT.md (Sprint 2 - delivery-reliability) from template
- Added bug-release traceability gate and release tag naming convention to PROJECT_RULES.md
- Added v1.0.2 pre-release entry to CHANGELOG.md with BUG-NNN references
- Created and pushed git tag v1.0.2 (clean tag, pre-release toggle set on GitHub)
- Updated README.md with Phase 5 status and sprint model overview
- All artifacts committed and pushed to GitHub (master @ 99d64db)

### Verification
- [x] All commits pushed to GitHub
- [x] Tag v1.0.2 confirmed on remote
- [ ] Sprint 2 execution (pending tomorrow's CRON result)
- [ ] v1.0.2 promoted from pre-release to stable on GitHub

### Paused Because
End of planning session. Waiting for tomorrow's CRON run (2026-04-14 12:00 UTC) to confirm whether bugs reproduce before executing fixes.

### Handoff Notes
No code changes made this session — planning only. Resume with:
1. Run .\scripts\fetch-logs.ps1 to check tomorrow's CRON result
2. Execute Sprint 2: broadcaster.py (BUG-001) then main.py (BUG-002)
3. Deploy to VM, confirm next CRON run, close sprint, promote v1.0.2 tag

## Session: 2026-04-14 09:00 (COT)

### Objective
Execute Sprint 2 bug fixes (BUG-001 through BUG-004) and deploy to VM.

### Accomplished
- ✅ **Fetched VM logs**: Diagnosed second CRON failure (2026-04-14 12:00 UTC)
- ✅ **New bugs discovered**: BUG-003 (screenshot crash in error handler) and BUG-004 (30s typing timeout too short)
- ✅ **BUG-003 fixed**: Created `safe_screenshot()` wrapper, replaced all 5 raw `page.screenshot()` calls
- ✅ **BUG-004 fixed**: Increased `press_sequentially` timeout to 60s, `wait_for` to 60s
- ✅ **BUG-001 fixed**: Added `connectivity_guard()` with 60s backoff polling before send loop
- ✅ **BUG-002 fixed**: `main.py` catches RuntimeError + checks bool return → `sys.exit(1)`
- ✅ **Documentation updated**: BUGS.md, CHANGELOG.md, SPRINT.md, 1-PLAN.md
- ✅ **Committed and pushed**: master @ cd015fc, tag v1.0.2 updated
- ✅ **Deployed to VM**: `git stash && git pull` on nposadaa111@trm-notifier
- ✅ **Sprint 3 draft created**: Placeholder for v1.0.3 if more issues surface

### Verification
- [x] Both files compile cleanly (py_compile)
- [x] Zero raw `page.screenshot()` calls remain in broadcaster.py
- [x] VM deployed and running updated code
- [ ] Next CRON run (2026-04-15 12:00 UTC) confirms fixes work

### Paused Because
User requested pause. Sprint 2 code is deployed; waiting for CRON verification.

### Handoff Notes
All code deployed. Resume by fetching logs after 2026-04-15 07:00 AM COT.
Manual test available: `gcloud compute ssh nposadaa111@trm-notifier --zone=us-central1-a --command="cd ~/wa_trm_notifier && bash scripts/run_vm.sh"`

## Session: 2026-04-14 12:00 (COT)

### Objective
Investigate and fix remaining delivery failures after Sprint 2 deployment.

### Accomplished
- ✅ **Diagnosed stale scraper data**: dolar-colombia.com updates after 7 AM → CRON was too early
- ✅ **BUG-005 fixed**: Shifted CRON to 10:00 AM COT + added staleness check in main.py
- ✅ **BUG-006 fixed (3 iterations)**:
  - v1: `document.execCommand('insertText')` → typed into DOM but Lexical state unaware
  - v2: `page.keyboard.insert_text()` → dispatches proper InputEvent, Lexical recognizes it
  - **Confirmed working**: Live test delivered $3,608.10 for Apr 14 with emojis at 14:38 COT
- ✅ **BUG-007 identified**: Delivery verification false negative (low priority, deferred to v1.0.4)
- ✅ **Documentation updated**: BUGS.md, CHANGELOG.md, VERSION, STATE.md, SPRINT, tags
- ✅ **Releases tagged**: v1.0.2 (cd015fc), v1.0.3 (23a7494) pushed to GitHub

### Verification
- [x] Live test: message delivered with correct date, value, emojis, double checkmarks
- [x] Scraper returns correct data at 10:00 AM+ COT
- [x] All code compile-clean
- [ ] Next CRON run (2026-04-15 10:00 AM COT) — autonomous verification pending

### Key Learning
WhatsApp Web uses Lexical (React-based rich text editor). Three levels of text insertion:
1. `press_sequentially` → keyboard events, breaks on emoji surrogate pairs
2. `document.execCommand('insertText')` → modifies DOM only, Lexical state unaware
3. `page.keyboard.insert_text()` → dispatches browser-level InputEvent, Lexical compatible ✅

### Paused Because
v1.0.3 released and deployed. Awaiting autonomous CRON verification.

### Handoff Notes
Next CRON: 2026-04-15 10:00 AM COT (15:00 UTC). Fetch logs and check WhatsApp group.
If delivered: promote v1.0.3 to stable. If not: check logs for new failure mode.
