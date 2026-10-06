# Technology Stack

> Refreshed on 2026-10-06 (milestone v1.2.0 completion)

## Runtime

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.10+ | Core runtime environment |

## Dependencies

### Production
| Package | Version | Purpose |
|---------|---------|---------|
| `requests` | Latest | HTTP client for Socrata API scraper |
| `beautifulsoup4` | Latest | HTML parsing library |
| `lxml` | Latest | Fast HTML/XML parser backend |
| `python-dotenv` | Latest | Environment variable loader |
| `playwright` | Latest | Browser automation framework |
| `playwright-stealth` | Latest | Stealth plugin for bot detection |

### Development / Testing
| Package | Version | Purpose |
|---------|---------|---------|
| `pytest` | 9.1.1 | Test framework (16 tests) |
| `black` | - | Code formatter (recommended) |
| `flake8` | - | Linter (recommended) |

## Infrastructure

| Service | Provider | Purpose |
|---------|----------|---------|
| GCP e2-micro | Google Cloud | Hosting VM for weekday-only cron runs |
| GitHub | GitHub | Source control and release tagging |
| Xvfb | Debian/Ubuntu | Virtual display server for headless browser |

## Configuration

| Variable | Purpose | Location |
|----------|---------|----------|
| `USER_DATA_DIR` | Playwright session data path | `broadcaster.py` |
| `RECIPIENTS_FILE` | Path to recipients configuration | `broadcaster.py` |
| `LOG_DIR` | Output directory for logic logs | `main.py` |

## External APIs

| API | Endpoint | Purpose |
|-----|----------|---------|
| Socrata (Superfinanciera) | `datos.gov.co` | TRM exchange rate data source |
