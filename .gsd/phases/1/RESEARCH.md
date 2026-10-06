# Phase 1 Research: SET-FX Spot Market Scraper

## Overview
This document outlines the findings for scraping and parsing Colombian USD/COP spot market indicators for the closing broadcast.

## Data Source
- **Provider**: SET-ICAP (official platform operator for the Colombian Foreign Exchange Spot Market — SET-FX).
- **Endpoint**: `https://proxy.icap.com.co/api/v1/ws/public/delay/snapshot?market=71`
- **Method**: HTTP `GET`
- **Authentication**: None required for the public delayed snapshot (15-min delay).
- **Format**: JSON

## Payload Inspection
The API response has the top-level structure:
```json
{
  "market": "71",
  "message_count": 10,
  "messages": [...]
}
```

Within `messages`, message with `id == 1008` ("Estadísticas") contains a list of market segment summaries. The USD/COP spot trading summary is identified by:
- `Merc.` == `"SPOT"`
- `Moneda` == `"USD/COP"`

Sample row:
```json
{
  "Merc.": "SPOT",
  "Moneda": "USD/COP",
  "Plazo": "0",
  "Monto Acumulado": "521853420.2600",
  "Apertura": "3179.2000",
  "Cierre": "3230.2500",
  "No Trans.": "577",
  "Promedio": "3210.8676",
  "Precio mínimo": "3035.0000",
  "Precio máximo": "3288.0000",
  "Monto promedio": "904425.3384",
  "Monto mínimo": "20.0000",
  "Monto máximo": "75000000.0000",
  "Monto último": "6000000.0000",
  "Fecha": "2026-10-06"
}
```

## Parsing & Normalization Considerations
1. **Accented Keys**: The keys for minimum and maximum prices contain Spanish diacritics (`Precio mínimo`, `Precio máximo`). Parsing must handle both literal unicode and normalized lowercase substrings (`minimo` / `maximo`).
2. **Numeric Types**: All numeric fields in the raw JSON are stringified floats. They must be safely converted to Python `float` or `int`.
3. **Derived Metrics**:
   - `change = cierre - apertura`
   - `change_pct = ((cierre - apertura) / apertura) * 100` (guarded against division by zero)
4. **Retry & Backoff**: Re-use the existing exponential backoff pattern from `scraper.py` (3 attempts, 3.0s initial delay with 2^n backoff).
5. **Market Closed / Edge Cases**: If the market is closed or no transactions occurred (e.g. holidays), `No Trans.` or prices may be 0.0 or the row may be absent; `scrape_spot_market()` must return a clear descriptive error dictionary rather than throwing unhandled exceptions.
