# Architecture

> Refreshed on 2026-10-06 (milestone v1.2.0 completion)

## Overview

The **TRM Notifier** is an automated system that scrapes the daily USD/COP exchange rate (TRM), enriches it with trend and weekly intelligence, and broadcasts it to WhatsApp contacts and groups via browser automation.

```text
┌─────────────────────────────────────────┐
│        [main.py] CLI Entry Point        │──────┐
│   • Daily TRM formatting & trend emoji  │      │
│   • Friday weekly summary trigger       │      │
├─────────────────────────────────────────┤      │
│     [scraper.py] TRM Scraper Logic      │      v
│   • Socrata API (datos.gov.co)          │   ┌────────────────────────────────┐
│   • Exponential backoff retries         │   │ [browser_config.py] Playwright │
│   • Weekly aggregation (limit=7)        │   │    Shared Hardening Config     │
├─────────────────────────────────────────┤   └────────────────────────────────┘
│  [broadcaster.py] Headless Automation   │◄──┘
│   • Keyboard-first search              │
│   • Checkmark verification             │
│   • Deduplication guard                 │
│   • Decryption sync self-healing        │
├─────────────────────────────────────────┤
│       [auth.py] Local UI Session        │
└─────────────────────────────────────────┘
```

## Components

### Main Orchestrator (`main.py`)
- **Purpose**: Coordinates the scraping and broadcasting lifecycle for cron/production execution.
- **Functionality**: Formats daily TRM with trend emoji (📈/📉), triggers Friday weekly summary block, invokes scraper and broadcaster.
- **Key flags**: `--dry-run`, `--force`, `--friday`.

### Scraper Logic (`scraper.py`)
- **Purpose**: Retrieves TRM exchange rate data from the Superfinanciera Socrata API (`datos.gov.co`).
- **Resilience**: Automatic retries with exponential backoff (3 attempts, 3s initial, 15s timeout) to absorb transient 502/503 errors.
- **Weekly mode**: `scrape_trm(limit=7)` returns `weekly_max`, `weekly_min`, `weekly_change`, `weekly_change_pct`, and `history` for Friday summaries.

### Browser Automation (`broadcaster.py`)
- **Purpose**: Automates WhatsApp Web to deliver messages natively to groups.
- **Role**: Strictly headless execution engine. Throws exception on unauthorized/QR states.
- **Key features**:
    - **Keyboard-First (DEC-016)**: Bypasses mouse click processing for search box interaction.
    - **Empirical Delivery (DEC-017)**: Verifies checkmarks in the DOM before reporting success.
    - **Deduplication Guard**: Checks last chat message before sending to prevent duplicate broadcasts.
    - **Decryption Self-Healing**: Reloads page on stuck sync instead of hard abort.

### Shared Browser Config (`browser_config.py`)
- **Purpose**: Universal config preventing divergence between local interactive and headless cloud sessions.
- **Role**: Chromium hardening (DEC-011, DEC-014), LevelDB lock sweeps, deep clean (never deletes Service Worker or IndexedDB).

### Local Session Authenticator (`auth.py`)
- **Purpose**: Dedicated CLI tool for capturing fresh QR-code tokens.
- **Role**: UI-only, waives timeouts for human phone scans (DEC-020).

## Data Flow

1. **Trigger**: `main.py` executed via `xvfb-run` on GCP VM (weekday-only CRON).
2. **Retrieval**: `scraper.py` fetches TRM from Socrata API with retry logic.
3. **Enrichment**: `main.py` adds trend emoji (📈/📉) by comparing with previous day. On Fridays, appends weekly High/Low/Trend summary block.
4. **Broadcast**: `broadcaster.py` navigates WhatsApp Web, deduplication-checks, keyboard-searches recipients, sends, and verifies delivery via checkmark detection.

## Integration Points

| Service | Type | Purpose |
|---------|------|---------|
| `datos.gov.co` (Socrata API) | REST API | Source of daily TRM values |
| `web.whatsapp.com` | Browser Automation | Broadcast delivery channel |
| `xvfb` | Virtual Display | Headless browser on GCP VM |

## Testing

- **Framework**: Pytest (16 tests, ~0.4s)
- **Coverage areas**:
  - Scraper retry/backoff logic (5 tests)
  - Friday summary detection & formatting (7 tests)
  - Broadcaster recovery & normalization (3 tests)
  - Duplicate prevention (1 test)

## Technical Debt

- [x] ~~Testing~~: Comprehensive test suite now in place (16 tests).
- [x] ~~Session Sync~~: Resolved via local-to-cloud transfer and `SingletonLock` cleanup.
- [ ] **Error Handling**: `scraper.py` could benefit from more granular error categorization.
- [ ] **Diagnostic Screenshots**: Accumulated `diag_*.png` files in project root should be moved to a dedicated directory.

## Conventions

**Naming**: Snake_case for Python scripts and functions; CAPS for configuration variables.
**Structure**: Flat root-level scripts for core functionality with `.gsd/` for project management.
**Testing**: Pytest with mocked external dependencies.
