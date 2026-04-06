---
phase: 4
plan: 2
wave: 2
dependencies: ["4.1"]
---

# Plan 4.2: WhatsApp Session Transfer + Cron Scheduling

## Objective
Transfer the WhatsApp session from local PC to the cloud VM, verify it works, and set up a daily cron job at 7:00 AM COT.

## Context
- .gsd/phases/4/RESEARCH.md
- broadcaster.py
- main.py

## Tasks

<task type="auto">
  <name>Transfer WhatsApp Session</name>
  <action>
    Option A — session transfer:
    1. On local PC: zip whatsapp_session/ folder
    2. SCP to VM: scp -i key.pem session.zip ubuntu@{IP}:~/wa_trm_notifier/
    3. Unzip on VM
    4. Test: xvfb-run python3 broadcaster.py --discovery
    
    Option B — if session doesn't transfer:
    1. Install noVNC or use SSH X11 forwarding
    2. Run broadcaster.py --discovery in headed mode
    3. Scan QR code via VNC
    4. Session now persisted on VM
  </action>
  <verify>xvfb-run python3 broadcaster.py --discovery shows chat list without QR scan</verify>
  <done>WhatsApp session active on VM, discovery mode lists chats</done>
</task>

<task type="auto">
  <name>Configure Cron + File Logging</name>
  <files>main.py</files>
  <action>
    1. Add Python logging to main.py (dual: console + logs/notifier_YYYY-MM-DD.log)
    2. Create logs/ dir, add to .gitignore
    3. Set up cron on VM:
       crontab -e
       0 12 * * 1-5 cd /home/ubuntu/wa_trm_notifier && xvfb-run python3 main.py >> logs/cron.log 2>&1
       (12:00 UTC = 7:00 AM COT, weekdays only)
    4. Commit logging changes, push to GitHub
  </action>
  <verify>crontab -l shows the scheduled job; logs/ directory exists</verify>
  <done>Cron registered. Next morning, log file shows successful TRM broadcast.</done>
</task>

<task type="auto">
  <name>Update Documentation</name>
  <files>.gsd/ROADMAP.md, .gsd/DECISIONS.md, README.md</files>
  <action>
    - Add DEC-008: Oracle Cloud chosen for deployment
    - Add DEC-009: Xvfb solves headless display requirement
    - Update ROADMAP Phase 4 status
    - Update README with cloud deployment section
  </action>
  <verify>grep "Oracle" README.md returns match</verify>
  <done>All docs reflect cloud deployment strategy</done>
</task>

## Success Criteria
- [ ] WhatsApp session working on cloud VM
- [ ] Cron job registered for 7:00 AM COT (12:00 UTC)
- [ ] File logging active
- [ ] Next-day verification: message sent automatically
