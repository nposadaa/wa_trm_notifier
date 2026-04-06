import os
from scraper import scrape_trm
from whatsapp_client import WhatsAppClient
from dotenv import load_dotenv

# Load credentials
load_dotenv()

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

    # 2. Prepare the WhatsApp Client
    client = WhatsAppClient()
    recipient = os.getenv("RECIPIENT_PHONE_NUMBER")
    
    # 3. Send the dynamic message
    # Template params: {{1}} = date, {{2}} = trm
    template_name = "trm_daily_official" 
    params = [trm_date, trm_value]
    
    if not all([client.access_token, client.phone_number_id, recipient]):
        print("Error: Missing credentials or recipient in .env file.")
        return

    success = client.send_template_message(
        recipient_number=recipient,
        template_name=template_name,
        language_code="en",
        params=params
    )
    
    if success:
        print("Task completed successfully!")
    else:
        print("Task failed during message submission.")

if __name__ == "__main__":
    main()
