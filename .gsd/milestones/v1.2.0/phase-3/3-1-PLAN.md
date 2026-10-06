---
phase: 3
plan: 1
wave: 1
---

# Plan 3.1: Weekly TRM Aggregation Module

## Objective
Extend `scraper.py` to fetch historical TRM data for weekly intelligence (last 5–7 trading days), computing weekly min, weekly max, and net weekly change metrics for Friday broadcasts.

## Context
- [.gsd/SPEC.md](file:///c:/Users/nposa/IT_Projects/wa_trm_notifier/.gsd/SPEC.md)
- [scraper.py](file:///c:/Users/nposa/IT_Projects/wa_trm_notifier/scraper.py)
- [tests/test_scraper_retry.py](file:///c:/Users/nposa/IT_Projects/wa_trm_notifier/tests/test_scraper_retry.py)

## Tasks

<task type="auto">
  <name>Extend scraper.py for weekly data aggregation</name>
  <files>scraper.py</files>
  <action>
    - Update `scrape_trm(max_retries=3, retry_delay=3.0, limit=7)` parameter to accept configurable data depth (default 7).
    - Parse the returned entries to calculate:
      - `weekly_max`: maximum float value across returned dataset.
      - `weekly_min`: minimum float value across returned dataset.
      - `weekly_start`: rate from the oldest entry in the window (e.g. 5–7 trading days back).
      - `weekly_change`: net difference (`trm - weekly_start`).
      - `weekly_change_pct`: percentage change `((trm - weekly_start) / weekly_start) * 100`.
    - Include these keys in the returned dictionary: `weekly_max`, `weekly_min`, `weekly_start`, `weekly_change`, `weekly_change_pct`, and `history` list.
    - Ensure backwards compatibility so existing keys (`trm`, `previous_trm`, `date`, `scraped_at`, `error`) remain identical.
  </action>
  <verify>.\venv\Scripts\python.exe -c "from scraper import scrape_trm; d=scrape_trm(limit=7); assert 'weekly_max' in d and 'weekly_min' in d and d['weekly_max'] >= d['weekly_min']"</verify>
  <done>scrape_trm(limit=7) returns weekly_max, weekly_min, weekly_change, and weekly_change_pct alongside standard single-day TRM data.</done>
</task>

<task type="auto">
  <name>Add unit tests for weekly scraper aggregation</name>
  <files>tests/test_scraper_retry.py</files>
  <action>
    - Add test function `test_scrape_trm_weekly_aggregation()` in `tests/test_scraper_retry.py`.
    - Mock `requests.get` returning 5 mock daily records.
    - Verify `weekly_max`, `weekly_min`, `weekly_change`, and `weekly_change_pct` are calculated accurately.
  </action>
  <verify>.\venv\Scripts\python.exe -m pytest tests/test_scraper_retry.py</verify>
  <done>All tests in test_scraper_retry.py pass with 100% assertion success on weekly calculations.</done>
</task>

## Success Criteria
- [ ] `scrape_trm(limit=7)` calculates weekly max, min, net change, and percentage change.
- [ ] Backward compatibility maintained for all single-day callers.
- [ ] Unit tests pass cleanly via `python -m pytest`.
