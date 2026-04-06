# Phase 4 Research: Automation & Deployment

## Constraint Analysis

| Requirement | GitHub Actions | Windows Task Scheduler | VPS (Linux + Xvfb) |
|-------------|---------------|----------------------|-------------------|
| Persistent WhatsApp session | No (ephemeral) | Yes | Yes |
| headless=False (DEC-007) | No display | Yes (user session) | Xvfb workaround |
| Free | Yes | Yes | No (~$5/mo) |
| Always-on | Yes | Only when PC on | Yes |
| Complexity | High (impossible) | Low | Medium |

## Decision: Windows Task Scheduler

**Why:** GitHub Actions is eliminated because:
1. Ephemeral containers = no persistent `./whatsapp_session/`
2. No display = headless only = WhatsApp blocks it
3. Would need QR scan every run (impossible in CI)

Windows Task Scheduler:
- Session already exists on this PC
- Can run `headless=False` with user logged in
- Free, zero infrastructure
- Cron-like scheduling via Task Scheduler

## Limitation
- PC must be on and user session active at scheduled time
- If PC sleeps/off, message skipped that day

## Implementation Approach
1. Create a `.bat` wrapper script that activates venv and runs `main.py`
2. Register a Windows Scheduled Task for 7:00 AM weekdays
3. Configure task to run only when user logged on (display needed)
4. Add logging to file for unattended run monitoring
