# STATE.md — Project Memory

> **Current Phase**: Phase 4 — Cloud Deployment
> **Last Update**: 2026-04-06
> **Status**: Active (resumed 2026-04-08)

## Current Position
- **Phase**: Phase 4 — Cloud Deployment (Stabilization & Scheduling)
- **Task**: Final Verification & Cron Setup
- **Status**: In Progress — Hardening Complete, Pending final delivery proof and automation.

## Last Session Summary
Successfully moved from "Failed Initialization" to "Fully Stabilized Broadcast" on GCP e2-micro. Resolved severe memory/GPU hangs and false-positive delivery reporting.

## In-Progress Work
The core broadcaster is now "Steel-Plated" for VM environments.
- **Verification Logic**: Checkmark-based auditing (DEC-017) ensures no false successes.
- **Input Logic**: Keyboard-only interaction for both search AND message composition (DEC-016, DEC-018).
- **Environment**: Keyring fixes and 3D shielding (DEC-011, DEC-012) fix persistence and GPU stalls.
- **Status**: First VM run completed (2026-04-08). Login ✅, Search ✅, Chat found ✅. Send FAILED — root cause identified as `fill()` bypassing React events. Fix applied (DEC-018). Re-verification pending.

## Next Steps
1. **Re-verify Send**: Re-run on VM with DEC-018 fix — expect `Clicking Send button icon...` and `Delivery Confirmed: Checkmark detected.`
2. **Cron Integration**: Map the `xvfb-run` command into a daily cron job on the VM.
3. **Failure Notifications**: Implement a simple email/webhook fallback if the Checkmark Audit (DEC-017) fails.
4. **Log Rotation**: Ensure `/logs` directory on VM doesn't saturate the disk.

## Decisions Made
- DEC-011: Local-to-Cloud session transfer is 10X more reliable than cloud-handshake for e2-micro VMs.
- DEC-012: Universal text-markers ("Unread") beat localized aria-labels for login detection.
- DEC-013: 4GB Swap is non-negotiable for stable Chromium rendering on e2-micro.
- DEC-016: Keyboard-first interaction (`focus()` + `keyboard.type()`) bypasses mouse-lag hangs on VM.
- DEC-017: Checkmark-based delivery audit prevents false-positive success reporting.
- DEC-018: `keyboard.type()` required for message composition — `fill()` bypasses React synthetic events on contenteditable divs.

## Blockers (Next Session Challenges)
- Potential rendering delays during first sync (solved with 120s timeout).
- Verification of recipients name matching (Wait for first sent message).

## Next Steps (Starting Point 🤝)
1. **The First Send**: Run the final script on the VM:
   `cd ~/wa_trm_notifier && git pull && source venv/bin/activate && xvfb-run --server-args="-screen 0 1024x768x24" python3 main.py --headless`
2. **Automate**: Once verified, set up crontab: `0 7 * * * cd ~/wa_trm_notifier && ./scripts/run_vm.sh`.
3. **Audit**: Complete Phase 4 documentation.
