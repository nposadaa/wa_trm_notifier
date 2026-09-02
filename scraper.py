import json
import logging
import time
from datetime import datetime
import requests

logger = logging.getLogger("trm_notifier")

def scrape_trm(max_retries: int = 3, retry_delay: float = 3.0):
    # Official SuperFinanciera TRM Open Data via Socrata
    url = "https://www.datos.gov.co/resource/mcec-87by.json?$limit=2&$order=vigenciadesde DESC"
    
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

