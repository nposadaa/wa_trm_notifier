# ROADMAP.md

> **Current Phase**: Phase 3 — Group Integration & Feasibility Check
> **Milestone**: v1.0 — Daily TRM Broadcast

## Must-Haves (from SPEC)
- [x] Automating Scraping logic (Python)
- [x] Integration with WhatsApp Business Cloud API
- [ ] Automated execution on a schedule (GitHub Actions)
- [ ] Group broadcast functionality

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

### Phase 3: Group Integration & Feasibility Check
**Status**: ⬜ Not Started
**Objective**: Determine the best path for group messaging based on your Meta account business status.
- [ ] Research/Test the Groups API with your current credentials.
- [ ] Pivot to 1-on-1 broadcasting or "Community" if direct group messaging is restricted.
- [ ] Update config to support multiple recipients/groups.

### Phase 4: Automation & Deployment (GitHub Actions)
**Status**: ⬜ Not Started
**Objective**: Move the service to the cloud for daily autonomous runs.
- [ ] Create `.github/workflows/daily_notifier.yml`.
- [ ] Set up GitHub Secrets for API tokens.
- [ ] Verify 7:00 AM cron schedule.
- [ ] Documentation for future updates.


