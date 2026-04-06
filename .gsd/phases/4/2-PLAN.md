---
phase: 4
plan: 2
wave: 2
dependencies: ["4.1"]
---

# Plan 4.2: Cloud Deployment (GCP Pivot)

## Objective
Deploy the TRM Notifier to a GCP e2-micro VM using stable "Local-to-Cloud" session transfer.

## Context
- .gsd/phases/4/GCP_SETUP.md (Finalized)
- Pivot from Oracle to GCP due to availability and bot-detection bypass requirements.

## Progress
- [x] Provision GCP VM (e2-micro, Ubuntu 22.04 LTS).
- [x] Configure 4GB Swap for memory stability.
- [x] Implement "Local-to-Cloud" session transfer (Linked locally, zipped, and uploaded).
- [x] Harden `broadcaster.py` with multi-language (Spanish) and role-based searching.
- [/] Verify first cloud broadcast (Final UI sync pending).
- [ ] Configure daily Cron job (7:00 AM COT).

## Tasks

<task type="auto">
  <name>Provision & Stabilize GCP VM</name>
  <action>
    1. Create e2-micro instance in us-central1-a.
    2. Add 4GB swap to prevent OOM crashes.
    3. Install: python3, pip, xvfb, playwright.
    4. Clone repo and setup venv.
  </action>
  <done>VM running with 4GB swap and all dependencies installed</done>
</task>

<task type="auto">
  <name>Session Transfer & UI Sync</name>
  <action>
    1. Link WhatsApp locally on laptop.
    2. Zip `whatsapp_session/` and upload to VM.
    3. Update `broadcaster.py` with "Universal" text-based login detection.
    4. Implement "Smart-Light" rendering and 1024x768 viewport.
  </action>
  <done>WhatsApp session active and searchable on VM</done>
</task>

<task type="auto">
  <name>Automation & Handover</name>
  <action>
    1. Test run: `xvfb-run ... main.py --headless`.
    2. Register crontab: `0 7 * * * ... ./scripts/run_vm.sh`.
    3. Final doc audit.
  </action>
  <done>Automated daily broadcast running from GCP cloud</done>
</task>

## Success Criteria
- [x] GCP VM provisioned and stable (Swap active).
- [x] WhatsApp session successfully transferred ("Login successful!").
- [/] First cloud send confirmed (Wait for tomorrow).
- [ ] Cron job registered for 7:00 AM COT.
