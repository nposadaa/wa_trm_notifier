# Plan 3.2 Summary: Friday Message Formatting & Trigger Logic

## Status: ✅ Complete

## What Was Done

### Task 1: Add --friday CLI flag and Friday Weekly Summary formatter to main.py
- Added `--friday` CLI argument to argparse for manual testing
- Friday detection: `get_cot_now().weekday() == 4` (auto) OR `args.friday` (manual override)
- On Friday, calls `scrape_trm(limit=7)` for weekly metrics
- Appends formatted weekly intelligence block to daily message:
  ```
  📊 *Resumen Semanal TRM*
  🔹 Máximo semana: $X,XXX.XX COP
  🔹 Mínimo semana: $X,XXX.XX COP
  📈/📉 Variación semanal: ±$XXX.XX (±X.XX%)
  ```
- Graceful degradation: if weekly API call fails, daily message is sent without weekly block
- Non-Friday runs are completely unaffected

### Task 2: Add unit tests for Friday Weekly Intelligence summary formatting
- Created `tests/test_friday_summary.py` with 7 tests:
  - `test_friday_flag_triggers_weekly_summary`: --friday flag works on non-Friday
  - `test_non_friday_no_weekly_summary`: No weekly block on regular days
  - `test_real_friday_auto_triggers_weekly`: Auto-detection on weekday=4
  - `test_weekly_max_min_in_message`: Max/min values correctly formatted
  - `test_weekly_trend_emoji_up`: Positive change shows 📈
  - `test_weekly_trend_emoji_down`: Negative change shows 📉
  - `test_weekly_data_unavailable_graceful`: Error fallback works

## Verification
- [x] `main.py --dry-run --friday` shows complete weekly summary block
- [x] `main.py --dry-run` (non-Friday) omits weekly block
- [x] pytest 16/16 passed (full suite)
