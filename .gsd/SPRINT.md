# Sprint 4 — Data Source Migration & Hardening

> **Duration**: 2026-04-17 to TBD
> **Status**: Planned
> **Target Release**: v1.0.4

## Goal
Migrate the TRM data source to the official SuperFinanciera Socrata API to eliminate data staleness, update the broadcast message template accordingly, and fix the pending delivery verification bug (BUG-007).

## Scope

### Included
- Refactor `scraper.py` to use `https://www.datos.gov.co/resource/mcec-87by.json` (SuperFinanciera official Open Data portal)
- Remove `BeautifulSoup` and `lxml` dependencies and parse JSON payload natively.
- Update message template string in `main.py`
- Fix delivery verification false-negatives in `broadcaster.py` by improving the CSS selectors and wait conditions (BUG-007).

### Explicitly Excluded
- New recipient support (Multi-recipient scheduling is a separate milestone).

## Tasks

| Task | Assignee | Status | Est. Hours |
|------|----------|--------|------------|
| FEATURE: Scraper migration to Socrata API | Claude | ⬜ Todo | 0.5 |
| FEATURE: Update message template in main.py | Claude | ⬜ Todo | 0.25 |
| BUG-007: Fix delivery verification in broadcaster.py | Claude | ⬜ Todo | 0.75 |

## Daily Log

### Day 1 (2026-04-17)
- Sprint created to address data staleness with `dolar-colombia.com` and transition to the official Datos Abiertos API.
- Included pending BUG-007 for delivery verification.

## Risks & Blockers

| Risk | Impact | Mitigation |
|------|--------|------------|
| Socrata API downtime | Med | Implement a try/except that attempts to fall back to the old web-scraping if the API is down (optional for v1). |
| Locator changes restrict verification | Low | Increase wait times and check for DOM structural markers instead of generic elements. |

## Retrospective (end of sprint)

### What Went Well
-

### What Could Improve
-

### Action Items
- [ ]

---

*Last updated: 2026-04-17*
