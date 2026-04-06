import os
import sys
import logging
import argparse
from datetime import datetime
from scraper import scrape_trm
from broadcaster import run_broadcaster

# --- Logging Setup ---
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
log_filename = os.path.join(LOG_DIR, f"notifier_{datetime.now().strftime('%Y-%m-%d')}.log")

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_filename, encoding="utf-8")
    ]
)
logger = logging.getLogger("trm_notifier")

def main():
    parser = argparse.ArgumentParser(description="TRM Notifier — Daily USD/COP Broadcaster")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode (production)")
    parser.add_argument("--discovery", action="store_true", help="List available WhatsApp chats")
    args = parser.parse_args()

    logger.info("--- Starting TRM Notifier ---")
    
    # 1. Scrape the data
    logger.info("Scraping TRM data...")
    trm_data = scrape_trm()
    
    if "error" in trm_data:
        logger.error(f"Error scraping TRM: {trm_data['error']}")
        return

    trm_value = trm_data["trm"]
    trm_date = trm_data["date"]
    logger.info(f"Scraped TRM: {trm_value} for date: {trm_date}")

    # 2. Format the Message
    message_text = f"📈 *TRM Oficial - {trm_date}*\n\n💵 Valor: ${trm_value:,.2f} COP. Source www.dolar-colombia.com"
    logger.info(f"Prepared Message:\n{message_text}")

    # 3. Broadcast using Playwright
    logger.info(f"Invoking Playwright Broadcaster (headless={args.headless})...")
    run_broadcaster(message_text, headless=args.headless, discovery_mode=args.discovery)
    
    logger.info("Task completed successfully!")

if __name__ == "__main__":
    main()

