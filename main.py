import os
from scraper import scrape_trm
from broadcaster import run_broadcaster

def main():
    print("--- Starting TRM Notifier ---")
    
    # 1. Scrape the data
    print("Scraping TRM data...")
    trm_data = scrape_trm()
    
    if "error" in trm_data:
        print(f"Error scraping TRM: {trm_data['error']}")
        return

    trm_value = trm_data["trm"]
    trm_date = trm_data["date"]
    print(f"Scraped TRM: {trm_value} for date: {trm_date}")

    # 2. Format the Message
    # We use some nice emojis to mimic the old template
    message_text = f"📈 *TRM Oficial - {trm_date}*\n\n💵 Valor: ${trm_value:,.2f} COP. Source www.dolar-colombia.com"
    print("\nPrepared Message:")
    print(message_text)
    print("")

    # 3. Broadcast using Playwright
    print("Invoking Playwright Broadcaster to send to groups...")
    run_broadcaster(message_text, headless=False, discovery_mode=False)
    
    print("Task completed successfully!")

if __name__ == "__main__":
    main()
