# Phase 4 Research: Cloud Deployment (Final)

## Confirmed: headless=True BLOCKED by WhatsApp
Tested 2026-04-06. Script ran but message not delivered. Need headless=False + Xvfb.

## All Options Ranked

### FREE TIER (Always Free)

| Provider | RAM | CPU | Storage | Xvfb OK? | Notes |
|----------|-----|-----|---------|----------|-------|
| **Oracle Cloud** | 24 GB (ARM) | 4 OCPU | 200 GB | Yes | Best free. "Out of capacity" risk |
| **Google Cloud** | 1 GB | shared | 30 GB | Tight | e2-micro. 1GB may OOM with Chromium |

### FREE TIER (12 months only)

| Provider | RAM | CPU | Storage | Notes |
|----------|-----|-----|---------|-------|
| **AWS EC2** | 1 GB | 1 vCPU | 30 GB | t2.micro. Charges after 12 months |
| **Azure** | 1 GB | 1 vCPU | 64 GB | B2pts. Charges after 12 months |

### PAID (Budget)

| Provider | Cost | RAM | Notes |
|----------|------|-----|-------|
| **IONOS** | ~$2/mo | 1 GB | Cheap but tight RAM |
| **RackNerd** | ~$2/mo | 1 GB | Annual promos via LowEndBox |
| **Vultr** | $2.50/mo | 512 MB | Too little RAM |
| **DigitalOcean** | $4/mo | 512 MB | Reliable but expensive for this |
| **Contabo** | $5/mo | 4 GB | Overkill but solid |
| **Hetzner** | $4/mo | 2 GB | Great value, no free tier |

### NOT VIABLE

| Provider | Why |
|----------|-----|
| Railway | No free tier. $5/mo min |
| Fly.io | No real free tier anymore |
| Render | Cron = paid. Free tier sleeps |
| PythonAnywhere | Can't run Playwright/browser |
| GitHub Actions | Ephemeral. No persistent session + no display |

## RAM Requirement
Chromium + Xvfb needs **min 1.5-2 GB RAM** to not OOM.
- Oracle (24GB) = massive overkill, perfect
- GCP e2-micro (1GB) = risky, may crash
- Budget VPS (1GB) = need swap file

## Recommendation

| Priority | Provider | Cost | Why |
|----------|----------|------|-----|
| 1st | **Oracle Cloud** | $0 | 24GB RAM, always free, best specs |
| 2nd | **Hetzner** | $4/mo | Reliable, 2GB RAM, great network |
| 3rd | **Contabo** | $5/mo | 4GB RAM, cheap for the specs |
| Fallback | **AWS EC2** | $0 (12mo) | Buys time, swap needed for 1GB |
