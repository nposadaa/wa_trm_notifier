---
phase: 2
plan: 1
wave: 1
status: complete
---

# Plan 2.1 Summary: Comparative Logic and Trend Emojis

## Completed Tasks
1. **Fetch previous TRM**: Updated `scraper.py` to use `$limit=2`. It now returns both the current TRM and the previous day's TRM.
2. **Implement dynamic emoji and dry-run**: Updated `main.py` to calculate a dynamic trend emoji (📈, 📉, ➖) and the rate delta. Also added a `--dry-run` flag to easily preview the message without interacting with WhatsApp.
3. **Fix Encoding**: Fixed a minor issue with the Windows terminal stdout character map to safely print emojis.

## Verification
- Both files successfully tested via `.\venv\Scripts\python.exe main.py --dry-run`.
- The log output properly formats the delta string and the trending emoji.
