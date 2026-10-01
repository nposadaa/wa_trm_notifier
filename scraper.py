import json
import logging
import time
from datetime import datetime
import requests

logger = logging.getLogger("trm_notifier")

def scrape_trm(max_retries: int = 3, retry_delay: float = 3.0, limit: int = 2):
    # Official SuperFinanciera TRM Open Data via Socrata
    # limit controls how many trading days to fetch (2 = daily, 7 = weekly)
    url = f"https://www.datos.gov.co/resource/mcec-87by.json?$limit={limit}&$order=vigenciadesde DESC"
    
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            if not data or len(data) == 0:
                raise ValueError("No data returned from Datos Abiertos API.")
                
            latest = data[0]
            
            # 1. Extract TRM numeric value
            trm_value = float(latest["valor"])
            
            # 2. Extract previous TRM numeric value
            if len(data) > 1:
                previous_trm = float(data[1]["valor"])
            else:
                previous_trm = trm_value
            
            # 3. Extract Date from vigenciadesde (e.g. "2026-04-17T00:00:00.000")
            reported_date = latest["vigenciadesde"].split("T")[0]
                
            result = {
                "trm": trm_value,
                "previous_trm": previous_trm,
                "date": reported_date,
                "scraped_at": datetime.now().isoformat()
            }
            
            # 4. Weekly aggregation when more than 2 records are requested
            if limit > 2 and len(data) > 1:
                values = [float(entry["valor"]) for entry in data]
                weekly_start = values[-1]  # oldest entry in the window
                result["weekly_max"] = max(values)
                result["weekly_min"] = min(values)
                result["weekly_start"] = weekly_start
                result["weekly_change"] = round(trm_value - weekly_start, 2)
                result["weekly_change_pct"] = round(
                    ((trm_value - weekly_start) / weekly_start) * 100, 4
                )
                result["history"] = [
                    {"date": entry["vigenciadesde"].split("T")[0], "value": float(entry["valor"])}
                    for entry in data
                ]
            
            return result

        except Exception as e:
            last_error = e
            if attempt < max_retries:
                backoff = retry_delay * (2 ** (attempt - 1))
                logger.warning(
                    f"TRM scrape attempt {attempt}/{max_retries} failed: {e}. Retrying in {backoff:.1f}s..."
                )
                time.sleep(backoff)
            else:
                logger.error(f"TRM scrape failed after {max_retries} attempts: {e}")

    return {"error": str(last_error)}

if __name__ == "__main__":
    trm_data = scrape_trm()
    print(json.dumps(trm_data, indent=2))

