# ROADMAP.md

> **Current Milestone**: v1.1 — Financial Intelligence
> **Goal**: Enhance the notification with trend analysis, historical context, and optimized delivery.

## Must-Haves
- [ ] Trend Indicator Emoji (📈/📉)
- [ ] Weekday-only CRON Schedule
- [ ] Friday Weekly Summary Message

## Phases (Milestone v1.1)

### Phase 1: Scheduling & Optimization
**Status**: ⬜ Not Started
**Objective**: Adjust scheduling to exclude weekends and save resources.
- [ ] Modify CRON expression on GCP VM.
- [ ] Update `run_vm.sh` or `main.py` to handle skip logic if necessary.

### Phase 2: Comparative Logic
**Status**: ⬜ Not Started
**Objective**: Implement historical data fetching to compare today's rate with the previous trading day.
- [ ] Update `scraper.py` to fetch previous day's data.
- [ ] Implement emoji logic in `main.py`.

### Phase 3: Weekly Intelligence
**Status**: ⬜ Not Started
**Objective**: Create a specialized summary message for Fridays.
- [ ] Build weekly aggregator for High/Low/Trend.
- [ ] Implement Friday-specific broadcast logic.

### Phase 4: Historical Deep-Dive
**Status**: ⬜ Not Started
**Objective**: Add 5-year historical alerts for max/min rates.
- [ ] Implement 5-year data fetch from Socrata API.
- [ ] Add "5 YEAR HISTORICAL" alert formatting.

---

## Milestone Archive

### v1.0 — Daily TRM Broadcast
**Status**: ✅ Complete (v1.0.8 stable)
**Objective**: Automate daily TRM notifications via WhatsApp Playwright on GCP.
- [x] **Phase 1-3**: Local foundation, Meta API pivot to Playwright.
- [x] **Phase 4**: GCP VM Deployment & Xvfb automation.
- [x] **Phase 5**: Stability hardening (Auto-cleanup, emoji-neutral verification).
