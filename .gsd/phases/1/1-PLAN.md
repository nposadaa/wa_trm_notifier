---
phase: 1
plan: 1
wave: 1
---

# Plan 1.1: SET-FX Spot Market Scraper

## Objective
Implement and unit-test a robust spot market scraper (`scrape_spot_market()`) that extracts Colombian USD/COP spot indicators (Apertura, Cierre, Promedio, Mínimo, Máximo, Variación, and Transacciones) from the official SET-ICAP delayed snapshot endpoint with exponential backoff retries and zero regression to existing functionality.

## Context
- `.gsd/SPEC.md`
- `.gsd/ROADMAP.md`
- `.gsd/phases/1/RESEARCH.md`
- `scraper.py`
- `tests/test_scraper_retry.py`
- `tests/test_friday_summary.py`

## Tasks

<task type="auto">
  <name>Implement scrape_spot_market in scraper.py</name>
  <files>scraper.py</files>
  <action>
    Add `scrape_spot_market(max_retries: int = 3, retry_delay: float = 3.0) -> dict` to `scraper.py`:
    1. Target endpoint: `https://proxy.icap.com.co/api/v1/ws/public/delay/snapshot?market=71` with standard User-Agent headers.
    2. Retry with exponential backoff matching the existing `scrape_trm` convention (attempt loop, backoff multiplier, error logging).
    3. Parse the JSON response:
       - Locate message with `id == 1008`.
       - Filter `result` array for entry where `row.get("Merc.") == "SPOT"` and `row.get("Moneda") == "USD/COP"`.
       - Safely extract values handling accented/unaccented keys (`Precio mínimo` / `Precio máximo`).
       - Convert numeric string values to floats/ints (`cierre`, `apertura`, `promedio`, `minimo`, `maximo`, `transacciones`, `monto_acumulado`, `fecha`).
       - Compute derived fields: `change` (`cierre - apertura`), `change_pct` (`((cierre - apertura) / apertura) * 100`), and `scraped_at`.
    4. Handle missing data, empty responses, or market-closed states gracefully by returning a structured dictionary with an `"error"` key.
    5. Ensure existing `scrape_trm()` remains untouched and fully compatible.
  </action>
  <verify>.\venv\Scripts\python.exe -c "from scraper import scrape_spot_market; res = scrape_spot_market(); print(res); assert 'cierre' in res or 'error' in res"</verify>
  <done>`scrape_spot_market()` is callable, executes without unhandled exceptions, and returns normalized dictionary with spot metrics or structured error.</done>
</task>

<task type="auto">
  <name>Create unit tests for spot market scraper</name>
  <files>tests/test_spot_scraper.py</files>
  <action>
    Create comprehensive unit tests in `tests/test_spot_scraper.py`:
    1. Test happy path parsing: Mock a successful SET-ICAP response and verify exact extracted values for `cierre`, `apertura`, `promedio`, `minimo`, `maximo`, `change`, `change_pct`, and `transacciones`.
    2. Test key normalization: Verify accented (`Precio mínimo`) and unaccented or alternate spellings are correctly extracted.
    3. Test missing SPOT row: Mock response without `USD/COP SPOT` row and assert structured error response.
    4. Test retry on HTTP errors: Mock temporary failure (e.g. 500 status code) followed by success to verify exponential backoff retry.
    5. Test fatal connection error: Mock persistent failure to verify clean error return after `max_retries`.
    6. Non-regression validation: Run the full pytest test suite to ensure all existing 16 tests (including `test_friday_summary.py`) continue to pass.
  </action>
  <verify>.\venv\Scripts\python.exe -m pytest tests/test_spot_scraper.py tests/test_friday_summary.py</verify>
  <done>All spot scraper tests pass and all Friday summary tests remain 100% passing without regression.</done>
</task>

## Success Criteria
- [ ] `scrape_spot_market()` successfully parses real and mocked SET-ICAP data.
- [ ] Network failures and missing payloads return structured errors without crashing.
- [ ] Unit tests in `tests/test_spot_scraper.py` pass.
- [ ] Full existing test suite (including Friday summary) passes with zero regressions.
