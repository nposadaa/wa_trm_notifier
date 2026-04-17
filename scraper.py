import requests
import json
from datetime import datetime

def scrape_trm():
    # Official SuperFinanciera TRM Open Data via Socrata
    url = "https://www.datos.gov.co/resource/mcec-87by.json?$limit=1&$order=vigenciadesde DESC"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if not data or len(data) == 0:
            raise ValueError("No data returned from Datos Abiertos API.")
            
        latest = data[0]
        
        # 1. Extract TRM numeric value
        trm_value = float(latest["valor"])
        
        # 2. Extract Date from vigenciadesde (e.g. "2026-04-17T00:00:00.000")
        reported_date = latest["vigenciadesde"].split("T")[0]
            
        result = {
            "trm": trm_value,
            "date": reported_date,
            "scraped_at": datetime.now().isoformat()
        }
        
        return result

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    trm_data = scrape_trm()
    print(json.dumps(trm_data, indent=2))
