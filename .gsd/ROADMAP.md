# ROADMAP.md

> **Current Phase**: Phase 3 — Group Integration & Feasibility Check
> **Milestone**: v1.0 — Daily TRM Broadcast

## Must-Haves (from SPEC)
- [x] Automating Scraping logic (Python)
- [x] Integration with WhatsApp Playwright Automation (Browser bypass for groups)
- [ ] Automated execution on a schedule (GitHub Actions)
- [ ] Native forwarding to multiple recipients/groups

## Phases

### Phase 1: Local Foundation & Scraper
**Status**: ✅ Complete
**Objective**: Build a robust Python scraper to get TRM data from the web.
- [x] Set up Python environment.
- [x] Implement scraper for `dolar-colombia.com`.
- [x] Local testing of output.

### Phase 2: 1-on-1 API Handshake & Template Registration
**Status**: ✅ Complete
**Objective**: Connect to the Meta Cloud API and send a "Hello World" notification to your test number.
- [x] Configure Meta Developer App credentials (`.env`).
- [x] Register and verify a TRM-specific Message Template.
- [x] Implement `whatsapp_client.py` for 1-on-1 messaging.
- [x] Test delivery to your test phone number.

### Phase 3: Direct Playwright Broadcast Pivot (Phase 3.3)
**Status**: ✅ Complete
**Objective**: Automate WhatsApp Web using Python + Playwright to completely bypass the Meta Cloud API.
- [x] Setup Playwright and Stealth context.
- [x] Initialize persistent WhatsApp session via manual QR scan.
- [x] Remove Meta API dependency (`whatsapp_client.py`).
- [x] Refactor `forwarder.py` to `broadcaster.py`, directly injecting formatted strings into the chat inputs.
- [x] Final E2E test verifying end-to-end direct delivery.

### Phase 4: Cloud Deployment (Oracle Cloud + Xvfb)
**Status**: 🚧 Planned
**Objective**: Deploy to Oracle Cloud Always Free VM for daily autonomous runs.
- [ ] Provision Oracle Cloud VM (Ubuntu ARM, Always Free).
- [ ] Install Python3, Playwright, Xvfb on VM.
- [ ] Transfer WhatsApp session from local PC to VM.
- [ ] Configure cron job for 7:00 AM COT (12:00 UTC).
- [ ] Add file logging for unattended monitoring.
- [ ] Update all documentation.


