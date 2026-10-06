---
phase: 2
plan: 1
wave: 1
---

# Plan 2.1: Comparative Logic and Trend Emojis

## Objective
Fetch the previous day's TRM to compare against the current TRM, and add a dynamic trend emoji (📈 or 📉) along with the delta to the WhatsApp broadcast message.

## Context
- .gsd/ROADMAP.md
- scraper.py
- main.py

## Tasks

<task type="auto">
  <name>Fetch previous TRM</name>
  <files>scraper.py</files>
  <action>
    Update the Socrata API URL in `scrape_trm()` to use `$limit=2` instead of `$limit=1`.
    Extract the numeric value from the second record (`data[1]`) as `previous_trm`.
    Handle the edge case where `len(data) < 2` by setting `previous_trm` equal to the current `trm_value`.
    Add `"previous_trm": previous_trm` to the returned `result` dictionary.
  </action>
  <verify>python scraper.py</verify>
  <done>Running scraper.py prints JSON containing both `trm` and `previous_trm`.</done>
</task>

<task type="auto">
  <name>Implement dynamic emoji and dry-run</name>
  <files>main.py</files>
  <action>
    Add a `--dry-run` flag to the `argparse` setup (`help="Print message and exit without sending"`).
    Extract `previous_trm` from `trm_data`.
    Determine the `trend_emoji`: 
    - If `trm_value > previous_trm`, use `📈`
    - If `trm_value < previous_trm`, use `📉`
    - Else, use `➖`
    Calculate the difference `delta = abs(trm_value - previous_trm)`.
    Update `message_text` to replace the hardcoded `📈` with `{trend_emoji}`.
    Update the message to include the delta, e.g., `Valor: $4,100.00 COP (+ $50.00)` (use `+` if up, `-` if down, or nothing if equal).
    Before calling `run_broadcaster`, if `args.dry_run` is True, print a log indicating dry run and `return` to prevent sending the WhatsApp message.
  </action>
  <verify>python main.py --dry-run</verify>
  <done>main.py calculates the correct emoji and delta and exits without calling the broadcaster.</done>
</task>

## Success Criteria
- [ ] `scraper.py` successfully fetches the previous day's TRM.
- [ ] `main.py` dynamically chooses the trend emoji based on comparison.
- [ ] `main.py` can be executed with `--dry-run` to view the message safely.
