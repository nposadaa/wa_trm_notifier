# STATE.md — Project Memory

> **Current Phase**: Phase 4 — Cloud Deployment
> **Last Update**: 2026-04-08
> **Status**: Active (resumed 2026-04-08T16:33-05:00)

## Current Position
- **Phase**: Phase 4 — Cloud Deployment (Stabilization & Scheduling)
- **Task**: Re-verify first live send with DEC-018 fix
- **Status**: Paused — DEC-018 fix committed and pushed. Re-run on VM is the immediate next action.

## Last Session Summary
- First live VM run executed. Login ✅ Search ✅ Chat opened ✅ — but message send ❌.
- Root cause identified: `chat_box.fill()` bypasses React synthetic events on WhatsApp Web's contenteditable div. Send button never activated.
- Fix applied: replaced `fill()` with `page.keyboard.type(delay=30)` — same keyboard-first pattern as DEC-016 (search), now extended to message composition (DEC-018).
- PROJECT_RULES.md updated: DECISIONS.md gate now canonical rule — no technical decision committed without DEC-NNN entry.
- All 3 commits pushed to GitHub (origin/master synced).

## In-Progress Work
- `broadcaster.py` — DEC-018 fix applied and committed. Re-verification on VM pending.
- No uncommitted changes. Working tree clean.

## Files of Interest
- `broadcaster.py` lines 329–380 — message composition + send + checkmark verification logic
- `.gsd/DECISIONS.md` — DEC-001 through DEC-018 fully documented
- `scripts/run_vm.sh` — the VM launch wrapper (use this for background runs post-verification)
- `recipients.json` — contains `"COP/USD Notifier"` (gitignored, exists only on VM and locally)

## Context Dump

### Exact VM Run Command (Next Session Start)
```bash
cd ~/wa_trm_notifier
git pull
pkill -f Xvfb || true
pkill -f chromium || true
rm -f ~/wa_trm_notifier/whatsapp_session/SingletonLock
source venv/bin/activate
xvfb-run --server-args="-screen 0 1024x768x24" python3 main.py --headless
```

### Expected Success Log (Post-DEC-018)
```
Login successful! Chat pane found.
Executing keyboard-only search for: COP/USD Notifier...
SUCCESS: Clicked COP/USD Notifier via Sidebar match (1/3).
Found chat box via Role.
Typing message to COP/USD Notifier...
Clicking Send button icon...          ← NEW: button now activates
[Ns] Delivery Confirmed: Checkmark detected.
✅ SUCCESS: Sent message to COP/USD Notifier!
```

### What Was Tried This Session
- `fill()` for message composition → FAILED (React event bypass, Send button never visible)
- `keyboard.type(delay=30)` → Applied, NOT yet verified on VM

### Data Security Confirmed
- `.env` → gitignored ✅
- `recipients.json` → gitignored ✅
- `whatsapp_session/` → gitignored ✅
- `session.zip` → gitignored ✅
- `logs/` + `*.png` → gitignored ✅

## Next Steps
1. `git pull` on VM + run command above → verify `Clicking Send button icon...` appears
2. Once first send confirmed → set up cron: `0 7 * * * cd ~/wa_trm_notifier && ./scripts/run_vm.sh`
3. Add log rotation (`logrotate` or simple cron daily cleanup)
4. Mark Phase 4 complete via `/complete-milestone`

