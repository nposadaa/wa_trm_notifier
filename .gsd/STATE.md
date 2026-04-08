# STATE.md — Project Memory

> **Current Phase**: Phase 4 — Cloud Deployment
> **Last Update**: 2026-04-08
> **Status**: Active

## Current Position
- **Phase**: Phase 4 — Cloud Deployment (Stabilization & Scheduling)
- **Task**: Final live execution of the headless Broadcaster
- **Status**: Structural blockers resolved. Awaiting user verification on VM.

## Last Session Summary
- Discovered and diagnosed a critical Chromium constraint: **Cross-OS Cryptography**. Zipped sessions from Windows DPAPI cannot be decrypted by Linux Ext4 Chrome, causing immediate 400 Bad Requests and access blocks.
- **Solution Executed (DEC-020)**: Architecture was split into two modules (`auth.py` and `broadcaster.py`) supported by `browser_config.py`.
- `auth.py` now runs strictly on the VM to capture the headless QR code, avoiding cross-OS contamination entirely.
- `broadcaster.py` was stripped of its interactive QR logic, making it a rugged headless-only execution worker.
- Documented Cron workflow securely in `CRON_SETUP.md`.

## In-Progress Work
- None. Codebase is clean. The system is structurally ready for the production Cron test.

## Files of Interest
- `broadcaster.py` — Native headless payload loop.
- `auth.py` — Dedicated UI / headless server session capturer.
- `browser_config.py` — Hardware limitation (e2-micro) hardening.
- `docs/SESSION_TRANSFER.md` — The guide defining how Chromium keys restrict OS transfers.
- `.gsd/DECISIONS.md` — DEC-019 to DEC-020 fully documented.

## Context Dump

### Exact VM Run Command (For the upcoming session test)
```bash
xvfb-run --server-args="-screen 0 1024x768x24" python3 main.py --headless
```

### Expected Success Log
```
[config] Launching Playwright browser (headless=True) with session at ./whatsapp_session...
Session fully stabilized. Waiting 5s for React UI to settle...
Loaded 1 recipients from recipients.json.
--- Processing: COP/USD Notifier ---
Executing keyboard-only search for: COP/USD Notifier...
SUCCESS: Clicked COP/USD Notifier via Text fallback
Found chat box successfully.
Typing message to COP/USD Notifier...
Send button icon not visible. Forcing focus and Enter key...
Verifying delivery to COP/USD Notifier...
✅ SUCCESS: Sent message to COP/USD Notifier!
```

## Next Steps
1. User tests `main.py` execution natively on the VM after generating `qr.png` via `auth.py`.
2. Confirm empirical delivery checkmarks function smoothly without memory stall timeouts.
3. Mark Phase 4 complete via `/complete-milestone` and close the sprint.
