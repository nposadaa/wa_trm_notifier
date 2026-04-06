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

def run_broadcaster(message_text="", headless=False, discovery_mode=False):
    """
    Launches WhatsApp Web with a persistent session.
    If discovery_mode is True, it will print the names of available chats.
    Otherwise, it loops through recipients, finds their chat, and sends `message_text`.
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

        if not message_text:
            print("CRITICAL: message_text is empty. Nothing to broadcast.")
            context.close()
            return

        if not os.path.exists(RECIPIENTS_FILE):
             print(f"Error: {RECIPIENTS_FILE} not found.")
             context.close()
             return
             
        with open(RECIPIENTS_FILE, "r") as f:
            data = json.load(f)
            recipients = data.get("recipients", [])
            
        print(f"Loaded {len(recipients)} recipients from {RECIPIENTS_FILE}.")

        # --- Direct Broadcasting Logic ---
        for rec in recipients:
            name = rec.get("name")
            print(f"--- Processing: {name} ---")
            
            # 1. Focus the main search box
            search_box = None
            selectors_to_try = [
                'input[data-tab="3"]',
                'input[placeholder="Search or start a new chat"]',
                'input[aria-label="Search or start a new chat"]',
                'div[contenteditable="true"][data-tab="3"]', # legacy fallback
                'div[aria-label="Search input textbox"]'
            ]

            for selector in selectors_to_try:
                try:
                    search_box = page.wait_for_selector(selector, state="visible", timeout=3000)
                    if search_box:
                        break
                except Exception:
                    continue
                    
            if not search_box:
                print("CRITICAL: Main search box not found. The WhatsApp Web DOM has changed.")
                continue
                
            # Clear search box and type the recipient name carefully
            search_box.fill("")
            time.sleep(0.5)
            search_box.type(name, delay=50) # typing like a human
            time.sleep(2) # wait for results to populate
            
            # 2. Click the chat in the search results pane
            # Often it appears in a pane with `span[title="Chat Name"]`
            try:
                chat_title = page.locator(f'span[title="{name}"]')
                chat_title.first.click(timeout=5000)
                time.sleep(1.5) # Wait for right pane to load
            except Exception as e:
                print(f"Could not find chat in search results for: {name}. Skipping.")
                # Clear search so it doesn't pollute next iteration
                search_box.fill("")
                continue

            # 3. Focus the chat input box (bottom bar of right pane)
            print(f"Typing message to {name}...")
            chat_box_selectors = [
                'div[aria-label="Type a message"]',
                'div[title="Type a message"]',
                'p.selectable-text.copyable-text',
                'div[contenteditable="true"][data-tab="10"]'
            ]
            
            chat_box = None
            for sel in chat_box_selectors:
                try:
                    # Look inside the main panel to make sure we don't grab something else
                    chat_box = page.wait_for_selector(f'#main {sel}', state="visible", timeout=2000)
                    if chat_box: break
                except:
                    # fallback to generic query
                    try:
                        chat_box = page.wait_for_selector(sel, state="visible", timeout=1000)
                        if chat_box: break
                    except: continue
                    
            if not chat_box:
                 print(f"Could not find the chat input box for {name}.")
                 continue
                 
            # 4. Fill message and send
            chat_box.fill("")
            # In Playwright, .fill() handles text nicely including newlines. 
            chat_box.fill(message_text)
            time.sleep(1) # Breathe
            chat_box.press("Enter")
            print(f"Sent message to {name}!")
            time.sleep(2) # Wait a bit before moving to next person

        print("\nAll recipients processed. Closing session.")
        context.close()

if __name__ == "__main__":
    import sys
    # Check for flags
    disco = "--discovery" in sys.argv
    run_broadcaster(message_text="Discovery Test", headless=False, discovery_mode=disco)
