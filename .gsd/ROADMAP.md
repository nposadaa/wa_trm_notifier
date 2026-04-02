# ROADMAP.md

> **Current Phase**: Phase 0 — Initialization
> **Milestone**: v1.0 — Daily TRM Broadcast

## Must-Haves (from SPEC)
- [ ] Automating Scraping logic (Python)
- [ ] Integration with WhatsApp Business Cloud API
- [ ] Automated execution on a schedule (GitHub Actions)
- [ ] Group broadcast functionality

## Phases

### Phase 1: Local Foundation & Scraper
**Status**: ⬜ Not Started
**Objective**: Build a robust Python scraper to get TRM data from the web.
- [ ] Set up Python environment.
- [ ] Implement scraper for `dolar-colombia.com`.
- [ ] Local testing of output.

### Phase 2: WhatsApp Cloud API Integration
**Status**: ⬜ Not Started
**Objective**: Connect the script to the Meta Cloud API to send notifications.
- [ ] Configure Meta Developer App.
- [ ] Verify message template ("Today's TRM is {{1}}").
- [ ] Implement `send_message` logic in Python.
- [ ] Test notification delivery to your personal chat.

### Phase 3: Group Connectivity
**Status**: ⬜ Not Started
**Objective**: Map and send to your target WhatsApp Groups.
- [ ] Retrieve Group IDs using the Groups API.
- [ ] Update config to include target group list.
- [ ] Test group broadcasting.

### Phase 4: Automation & Deployment (GitHub Actions)
**Status**: ⬜ Not Started
**Objective**: Move the service to the cloud for daily autonomous runs.
- [ ] Create `.github/workflows/daily_notifier.yml`.
- [ ] Set up GitHub Secrets for API tokens.
- [ ] Verify 7:00 AM cron schedule.
- [ ] Documentation for future updates.

