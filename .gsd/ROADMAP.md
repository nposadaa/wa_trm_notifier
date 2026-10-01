# ROADMAP.md

> **Current Milestone**: v1.1.0 — Financial Intelligence
> **Goal**: Enhance the notification with trend analysis, historical context, and optimized delivery.

## Must-Haves
- [ ] Trend Indicator Emoji (📈/📉)
- [ ] Weekday-only CRON Schedule
- [x] Friday Weekly Summary Message

## Phases (Milestone v1.1.0)

### Phase 1: Scheduling & Optimization
**Status**: ✅ Complete
**Objective**: Adjust scheduling to exclude weekends and save resources.
- [ ] Modify CRON expression on GCP VM.
- [ ] Update `run_vm.sh` or `main.py` to handle skip logic if necessary.

### Phase 2: Comparative Logic
**Status**: ✅ Complete
**Objective**: Implement historical data fetching to compare today's rate with the previous trading day.
- [x] Update `scraper.py` to fetch previous day's data.
- [x] Implement emoji logic in `main.py`.

### Phase 3: Weekly Intelligence
**Status**: ✅ Complete
**Objective**: Create a specialized summary message for Fridays.
- [x] Build weekly aggregator for High/Low/Trend.
- [x] Implement Friday-specific broadcast logic.

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
