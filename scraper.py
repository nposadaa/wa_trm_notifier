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

def scrape_spot_market(max_retries: int = 3, retry_delay: float = 3.0):
    """
    Scrape official USD/COP spot market indicators from the SET-ICAP delayed snapshot API.
    Returns a dictionary with spot prices, daily variation, and volume, or an error dict.
    """
    url = "https://proxy.icap.com.co/api/v1/ws/public/delay/snapshot?market=71"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            if not data or "messages" not in data:
                raise ValueError("No valid message payload returned from SET-ICAP API.")
                
            # Locate statistics message (id 1008)
            stats_rows = []
            for msg in data.get("messages", []):
                if msg.get("id") == 1008 and isinstance(msg.get("result"), list):
                    stats_rows.extend(msg["result"])
                    
            # Find the USD/COP SPOT row
            spot_row = None
            for row in stats_rows:
                if str(row.get("Merc.", "")).strip().upper() == "SPOT" and str(row.get("Moneda", "")).strip().upper() == "USD/COP":
                    spot_row = row
                    break
                    
            if not spot_row:
                raise ValueError("USD/COP SPOT market row not found in SET-ICAP response.")
                
            # Helper to find keys case-insensitively / with or without accents
            def get_val(key_fragment: str, default="0.0"):
                for k, v in spot_row.items():
                    if key_fragment.lower() in k.lower():
                        return v
                return default

            cierre = float(spot_row.get("Cierre", 0.0))
            apertura = float(spot_row.get("Apertura", 0.0))
            promedio = float(spot_row.get("Promedio", 0.0))
            minimo = float(get_val("mínimo", get_val("minimo", "0.0")))
            maximo = float(get_val("máximo", get_val("maximo", "0.0")))
            monto_acumulado = float(spot_row.get("Monto Acumulado", 0.0))
            
            raw_trans = spot_row.get("No Trans.", 0)
            transacciones = int(float(raw_trans)) if raw_trans else 0
            
            fecha = spot_row.get("Fecha", "")
            
            # Calculate daily variations vs apertura
            change = round(cierre - apertura, 2)
            if apertura > 0:
                change_pct = round(((cierre - apertura) / apertura) * 100, 4)
            else:
                change_pct = 0.0

            return {
                "cierre": cierre,
                "apertura": apertura,
                "promedio": promedio,
                "minimo": minimo,
                "maximo": maximo,
                "change": change,
                "change_pct": change_pct,
                "transacciones": transacciones,
                "monto_acumulado": monto_acumulado,
                "fecha": fecha,
                "scraped_at": datetime.now().isoformat(),
            }

        except Exception as e:
            last_error = e
            if attempt < max_retries:
                backoff = retry_delay * (2 ** (attempt - 1))
                logger.warning(
                    f"SET-ICAP spot scrape attempt {attempt}/{max_retries} failed: {e}. Retrying in {backoff:.1f}s..."
                )
                time.sleep(backoff)
            else:
                logger.error(f"SET-ICAP spot scrape failed after {max_retries} attempts: {e}")

    return {"error": str(last_error)}

if __name__ == "__main__":
    trm_data = scrape_trm()
    print("TRM Data:")
    print(json.dumps(trm_data, indent=2))
    print("\nSpot Data:")
    spot_data = scrape_spot_market()
    print(json.dumps(spot_data, indent=2))

