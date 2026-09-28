---
phase: 3
plan: 2
wave: 2
---

# Plan 3.2: Friday Message Formatting & Trigger Logic

## Objective
Update `main.py` to detect Friday executions (or `--friday` CLI flag), formatting and appending the Friday Weekly Intelligence Summary section to the daily broadcast message.

## Context
- [.gsd/SPEC.md](file:///c:/Users/nposa/IT_Projects/wa_trm_notifier/.gsd/SPEC.md)
- [main.py](file:///c:/Users/nposa/IT_Projects/wa_trm_notifier/main.py)
- [scraper.py](file:///c:/Users/nposa/IT_Projects/wa_trm_notifier/scraper.py)
- [tests/test_main_duplicate_prevention.py](file:///c:/Users/nposa/IT_Projects/wa_trm_notifier/tests/test_main_duplicate_prevention.py)

## Tasks

<task type="auto">
  <name>Add --friday CLI flag and Friday Weekly Summary formatter to main.py</name>
  <files>main.py</files>
  <action>
    - Add `--friday` CLI argument to `main.py` argparse for manual testing/overriding.
    - Check if today is Friday (`get_cot_now().weekday() == 4` or `args.friday`).
    - If Friday:
      - Call `scrape_trm(limit=7)` to obtain weekly metrics.
      - Append formatted Friday Weekly Intelligence section to `message_text`:
        ```text
        📊 *Resumen Semanal TRM*
        🔹 Máximo semana: ${weekly_max:,.2f} COP
        🔹 Mínimo semana: ${weekly_min:,.2f} COP
        {weekly_trend_emoji} Variación semanal: {weekly_sign}${abs(weekly_change):,.2f} ({weekly_change_pct:+.2f}%)
        ```
    - Maintain standard daily formatting for non-Friday runs.
  </action>
  <verify>.\venv\Scripts\python.exe main.py --dry-run --friday</verify>
  <done>Running `main.py --dry-run --friday` prints message output containing the "Resumen Semanal TRM" block with max, min, and weekly variation.</done>
</task>

<task type="auto">
  <name>Add unit tests for Friday Weekly Intelligence summary formatting</name>
  <files>tests/test_friday_summary.py</files>
  <action>
    - Create `tests/test_friday_summary.py`.
    - Test Friday detection logic (`weekday() == 4` or `--friday` flag).
    - Test message formatting includes `📊 *Resumen Semanal TRM*` and correct metrics when Friday flag is set.
    - Test message formatting omits Weekly Summary when executed on a non-Friday without `--friday` flag.
  </action>
  <verify>.\venv\Scripts\python.exe -m pytest tests/test_friday_summary.py</verify>
  <done>All tests in test_friday_summary.py pass cleanly via pytest.</done>
</task>

## Success Criteria
- [ ] `main.py --friday` generates Friday Weekly Intelligence Summary message block.
- [ ] Automated Friday runs (`weekday() == 4`) include weekly max, min, and net change.
- [ ] Non-Friday runs preserve standard daily message format without weekly block.
- [ ] All unit tests pass cleanly via `python -m pytest`.
