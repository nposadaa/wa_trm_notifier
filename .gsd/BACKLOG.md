# BACKLOG.md - Feature & Task Inventory

| ID | Feature | Phase | Size | Value | Status | Description |
|---|---|---|---|---|---|---|
| 1 | **Trend Indicator Emoji** | 2 | 3 | High | Complete | Add 📈 or 📉 to the daily message by comparing today's rate with the previous trading day. |
| 2 | **Weekday-only Schedule** | 1 | 1 | High | Complete | Adjust CRON/scheduling to exclude Saturdays and Sundays to save resources when the market is closed. |
| 3 | **Friday Weekly Summary** | 3 | 8 | Med | Backlog | Send a special "Weekly Summary" message on Fridays with Low/High rates and overall weekly trend. |
| 4 | **5-Year Historical Alert** | 4 | 5 | Med | Backlog | Analyze the last 5 years of data; if today is a historical max/min, add a red "5 YEAR HISTORICAL" alert title. |
| 5 | **Refactor Broadcaster Legacy Check** | 5 | 1 | Low | Backlog | Remove the legacy 'Emergency re-Enter' code in `broadcaster.py`, as it's been rendered redundant by the new 30s DOM polling logic from v1.1.1. |
| 6 | **Timezone-Aware Date Display** | 5 | 2 | High | Backlog | The VM runs in UTC, so evening COT runs (e.g., 7 PM May 14 = 00:00 May 15 UTC) cause the message to display tomorrow's date. Use `America/Bogota` timezone for determining today's date and selecting which rate to display. Affects `main.py` staleness check and message formatting. |
