import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def scrape_trm():
    url = "https://www.dolar-colombia.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "lxml")
        
        # 1. Extract TRM numeric value
        # Selector: span.exchange-rate
        trm_element = soup.select_one("span.exchange-rate")
        if not trm_element:
            raise ValueError("Could not find TRM element on the page.")
        
        trm_text = trm_element.get_text(strip=True)
        # Clean: remove commas and any whitespace
        trm_value = float(trm_text.replace(",", ""))
        
        # 2. Extract Date from input-datepicker
        # Selector: input.input-datepicker (value attribute)
        date_element = soup.select_one("input.input-datepicker")
        if not date_element or not date_element.get("value"):
            # Fallback to human-readable header if input fails
            fallback_date_element = soup.select_one("div.box__title")
            reported_date = fallback_date_element.get_text(strip=True) if fallback_date_element else "Unknown"
        else:
            reported_date = date_element.get("value")
            
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
