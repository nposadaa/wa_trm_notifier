---
phase: 4
plan: 1
wave: 1
---

# Plan 4.1: Cloud VM Provisioning + Environment Setup

## Objective
Provision an Oracle Cloud Always Free VM and configure it with Python, Playwright, and Xvfb for headless-display browser automation.

## Context
- .gsd/phases/4/RESEARCH.md
- requirements.txt

## Tasks

<task type="auto">
  <name>Provision Oracle Cloud VM</name>
  <action>
    Guide user through Oracle Cloud Console:
    1. Sign up at cloud.oracle.com (free account)
    2. Create Compute Instance: Shape = Ampere A1 (1 OCPU, 6GB RAM), Image = Ubuntu 22.04
    3. Generate SSH key pair, download private key
    4. Note public IP address
  </action>
  <verify>SSH into VM: ssh -i key.pem ubuntu@{IP}</verify>
  <done>Can SSH into running Ubuntu VM</done>
</task>

<task type="auto">
  <name>Install Dependencies on VM</name>
  <files>requirements.txt</files>
  <action>
    SSH into VM and run:
    ```bash
    sudo apt update && sudo apt upgrade -y
    sudo apt install -y python3-pip xvfb git
    git clone https://github.com/nposadaa/wa_trm_notifier.git
    cd wa_trm_notifier
    pip3 install -r requirements.txt
    playwright install chromium
    playwright install-deps
    ```
  </action>
  <verify>xvfb-run python3 -c "from playwright.sync_api import sync_playwright; print('OK')"</verify>
  <done>Playwright + Xvfb installed, import succeeds</done>
</task>

## Success Criteria
- [ ] Oracle Cloud VM running Ubuntu
- [ ] SSH access working
- [ ] Python3, Playwright, Xvfb installed
- [ ] Repo cloned on VM
