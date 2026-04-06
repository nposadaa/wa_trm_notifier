import os
import time
import json
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Configuration
USER_DATA_DIR = "./whatsapp_session"
WHATSAPP_URL = "https://web.whatsapp.com/"
RECIPIENTS_FILE = "recipients.json"

def run_forwarder(headless=False, discovery_mode=False):
    """
    Launches WhatsApp Web with a persistent session.
    If discovery_mode is True, it will print the names of available chats.
    Otherwise, it will attempt to find and forward the TRM message.
    """
    with sync_playwright() as p:
        # Launch persistent context
        print(f"Launching browser with session at {USER_DATA_DIR}...")
        context = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=headless,
            args=["--start-maximized"]
        )
        
        page = context.new_page()
        stealth = Stealth()
        stealth.apply_stealth_sync(page)
        
        print(f"Navigating to {WHATSAPP_URL}...")
        page.goto(WHATSAPP_URL)
        
        # Wait for the chat list to load (indicator of login)
        print("Waiting for WhatsApp Web to load. If this is your first run, please scan the QR code.")
        
        try:
            # Selector for the side panel (chat list)
            page.wait_for_selector('div[aria-label="Chat list"]', timeout=60000)
            print("Login successful or session restored!")
        except Exception as e:
            print("Timeout waiting for chat list. Please ensure you are logged in.")
            context.close()
            return

        if discovery_mode:
            print("\n--- DISCOVERY MODE ---")
            print("Fetching recent chat names...")
            time.sleep(5) # Wait for chats to populate
            chats = page.query_selector_all('span[title]')
            chat_names = set()
            for chat in chats:
                name = chat.get_attribute("title")
                if name:
                    chat_names.add(name)
            
            print("Found chats:")
            for name in sorted(chat_names):
                print(f" - {name}")
            print("----------------------\n")
            input("Press Enter to close discovery mode...")
            context.close()
            return

        # --- Forwarding Logic ---
        # 1. Search for the sender (Test Business Account)
        # Note: In WhatsApp Web, the search bar is usually a div with contenteditable
        search_box = page.wait_for_selector('div[contenteditable="true"][data-tab="3"]', state="visible", timeout=10000)
        if not search_box:
            search_box = page.wait_for_selector('div[contenteditable="true"][aria-autocomplete="list"]', timeout=10000)
        sender_name = "TRM Notifier Test" # Name of your Business account in WhatsApp UI
        print(f"Searching for chat: {sender_name}...")
        search_box.fill(sender_name)
        search_box.press("Enter")
        time.sleep(2)

        # 2. Find the last message and hover to show menu
        # This is the most brittle part as selectors change. 
        # We look for the last message in the conversation.
        messages = page.query_selector_all('div.message-in, div.message-out')
        if not messages:
            print("Could not find any messages in this chat.")
            context.close()
            return
        
        last_message = messages[-1]
        last_message.scroll_into_view_if_needed()
        last_message.hover()
        time.sleep(1)

        # 3. Click the 'dropdown' arrow for the message menu
        # This usually appears on hover.
        try:
            menu_button = last_message.wait_for_selector('span[data-icon="down-context"]', timeout=3000)
            menu_button.click()
            time.sleep(1)
            
            # 4. Click 'Forward' in the context menu
            forward_option = page.wait_for_selector('div[aria-label="Forward"]', timeout=3000)
            forward_option.click()
            time.sleep(1)

            # 5. Search for recipients and send
            # Load recipients from json
            if not os.path.exists(RECIPIENTS_FILE):
                print(f"Error: {RECIPIENTS_FILE} not found.")
                context.close()
                return
            
            with open(RECIPIENTS_FILE, "r") as f:
                data = json.load(f)
                recipients = data.get("recipients", [])

            for rec in recipients:
                name = rec.get("name")
                print(f"Forwarding to: {name}...")
                
                # Search for recipient in the forward modal
                forward_search = page.wait_for_selector('div[contenteditable="true"][data-tab="6"]') 
                forward_search.fill(name)
                time.sleep(1)
                
                # Select the first result
                # Selector for the contact in the selection list
                page.click(f'span[title="{name}"]')
                time.sleep(0.5)

            # 6. Click 'Send' forward button (the green arrow button)
            send_button = page.wait_for_selector('span[data-icon="send"]', timeout=5000)
            send_button.click()
            print("Forwarding complete!")
            time.sleep(2)

        except Exception as e:
            print(f"Failed during forwarding sequence: {e}")

        context.close()

if __name__ == "__main__":
    import sys
    # Check for flags
    disco = "--discovery" in sys.argv
    run_forwarder(headless=False, discovery_mode=disco)
