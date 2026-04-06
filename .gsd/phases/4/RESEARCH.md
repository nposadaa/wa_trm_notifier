# Phase 4 Research: Cloud Deployment Options

## Core Constraints (from DEC-007)
- Playwright needs `headless=False` (WhatsApp blocks headless)
- Persistent `./whatsapp_session/` directory required
- QR code scan needed once, then session reused
- Script runs ~2 min per execution

## Solution: Xvfb (X Virtual Framebuffer)
Linux tool that creates a **virtual display**. Lets `headless=False` work on servers with no monitor.
Command: `xvfb-run python main.py` — that simple.

## Cloud Options Ranked

| Provider | Cost | RAM | Storage | Always-On | Xvfb | Verdict |
|----------|------|-----|---------|-----------|------|---------|
| **Oracle Cloud (Always Free)** | $0 | 24 GB (ARM) | 200 GB | Yes | Yes | **BEST** |
| **Google Cloud (e2-micro)** | $0 | 1 GB | 30 GB | Yes | Yes | Viable but tight |
| **AWS EC2 (t2.micro)** | $0 (12 months) | 1 GB | 30 GB | 12 months only | Yes | Not permanent |
| **DigitalOcean** | $4/mo | 512 MB | 10 GB | Yes | Yes | Cheap paid option |
| **AWS Lightsail** | $3.50/mo | 512 MB | 20 GB | Yes | Yes | Cheap paid option |

## Recommendation: Oracle Cloud (Always Free)

**Why Oracle:**
- Truly always free (not time-limited like AWS)
- ARM Ampere A1: up to 4 OCPUs, 24 GB RAM — massive overkill for this script
- 200 GB storage — no session persistence issues
- Ubuntu available — easy Playwright + Xvfb setup

**Caveat:** "Out of Capacity" errors common in popular regions. May need to try different region.

## Fallback: Google Cloud e2-micro
- 1 GB RAM tight but enough for Chromium + Xvfb
- Truly always free
- More reliable availability than Oracle

## Implementation Architecture (Cloud)

```
Oracle Cloud VM (Ubuntu 22.04 ARM)
  |
  +-- cron (7:00 AM COT = 12:00 UTC)
  |     |
  |     +-- xvfb-run python3 main.py
  |           |
  |           +-- scraper.py (fetch TRM)
  |           +-- broadcaster.py (Playwright + WhatsApp Web)
  |
  +-- ./whatsapp_session/ (persistent on disk)
  +-- ./logs/ (daily log files)
```

### Setup Steps
1. Provision Oracle Cloud Always Free VM (Ubuntu, ARM)
2. Install Python3, pip, Playwright, Xvfb
3. Clone repo, install requirements
4. Transfer `whatsapp_session/` from local PC to VM
5. One-time: run with VNC/noVNC to verify session works (or re-scan QR)
6. Set up cron job: `0 12 * * * cd /home/ubuntu/wa_trm_notifier && xvfb-run python3 main.py >> logs/cron.log 2>&1`

### Session Transfer Strategy
- Zip `whatsapp_session/` from local Windows
- SCP to VM
- Test if session transfers across OS (Chromium profile should be cross-platform)
- If not: install noVNC on VM, connect browser, scan QR once
