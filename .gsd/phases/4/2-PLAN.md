---
phase: 4
plan: 2
wave: 2
dependencies: ["4.1"]
---

# Plan 4.2: Cloud Deployment

## Objective
Deploy to cloud based on headless test results from Plan 4.1.

## Context
- .gsd/phases/4/RESEARCH.md
- .gsd/phases/4/1-PLAN.md results

## Tasks

<task type="auto">
  <name>Provision Cloud VM</name>
  <action>
    Provision Oracle Cloud Always Free VM:
    1. Sign up at cloud.oracle.com
    2. Create Compute Instance: Ampere A1 (1 OCPU, 6GB RAM), Ubuntu 22.04
    3. SSH key pair setup
    4. Install: python3, pip, playwright, playwright-deps
    5. If headless=True failed: also install xvfb
    6. Clone repo, pip install -r requirements.txt, playwright install chromium
  </action>
  <verify>SSH into VM, run: python3 -c "from playwright.sync_api import sync_playwright; print('OK')"</verify>
  <done>VM running with all dependencies installed</done>
</task>

<task type="auto">
  <name>Session Setup + Cron</name>
  <action>
    Session setup on VM:
    - Option A (headless=True works): transfer storageState JSON from local
    - Option B (headless=False needed): install noVNC, scan QR via browser
    
    Cron setup:
    - crontab -e
    - If headless: `0 12 * * 1-5 cd ~/wa_trm_notifier && python3 main.py --headless`
    - If Xvfb: `0 12 * * 1-5 cd ~/wa_trm_notifier && xvfb-run python3 main.py`
    - Redirect output: >> logs/cron.log 2>&1
    - 12:00 UTC = 7:00 AM COT, weekdays only
  </action>
  <verify>crontab -l shows job; next morning check logs/cron.log for success</verify>
  <done>Automated daily broadcast running from cloud</done>
</task>

<task type="auto">
  <name>Update All Documentation</name>
  <files>.gsd/ROADMAP.md, .gsd/DECISIONS.md, README.md</files>
  <action>
    - Add DEC-008: Cloud provider choice + rationale
    - Add DEC-009: headless mode decision (based on test results)
    - Mark Phase 4 complete in ROADMAP
    - Add cloud deployment section to README
    - Git push all changes
  </action>
  <verify>grep "Oracle\|cloud\|deploy" README.md returns matches</verify>
  <done>All docs reflect final deployment architecture</done>
</task>

## Success Criteria
- [ ] Cloud VM provisioned and running
- [ ] WhatsApp session active on VM
- [ ] Cron job registered for 7:00 AM COT
- [ ] Next-day verification: message sent automatically from cloud
- [ ] All documentation updated
