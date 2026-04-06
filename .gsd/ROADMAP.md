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
**Status**: 🚧 In Progress
**Objective**: Automate WhatsApp Web using Python + Playwright to completely bypass the Meta Cloud API.
- [x] Setup Playwright and Stealth context.
- [x] Initialize persistent WhatsApp session via manual QR scan.
- [ ] Remove Meta API dependency (`whatsapp_client.py`).
- [ ] Refactor `forwarder.py` to `broadcaster.py`, directly injecting formatted strings into the chat inputs.
- [ ] Final E2E test verifying end-to-end direct delivery.

### Phase 4: Automation & Deployment (GitHub Actions)
**Status**: ⬜ Not Started
**Objective**: Move the service to the cloud for daily autonomous runs.
- [ ] Create `.github/workflows/daily_notifier.yml`.
- [ ] Set up GitHub Secrets for API tokens.
- [ ] Verify 7:00 AM cron schedule.
- [ ] Documentation for future updates.


