import os
import time
import json
from playwright.sync_api import sync_playwright
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
        # Define a modern User Agent to prevent the "Unsupported Browser" error
        USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"

        # Launch persistent context with ADVANCED HARDENING
        print(f"Launching hardened browser with session at {USER_DATA_DIR}...")
        context = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=headless,
            user_agent=USER_AGENT,
            viewport={'width': 1024, 'height': 768},
            # --- Anti-Detection: Locality matching ---
            timezone_id="America/Bogota",
            locale="es-419",
            # --- Memory & OOM flags ---
            args=[
                "--start-maximized",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-gpu",
                "--disable-extensions",
                "--no-zygote",
                "--js-flags='--max-old-space-size=512'", 
                "--disable-setuid-sandbox",
                "--no-first-run",
                "--disable-background-networking",
                "--disable-web-security"
            ]
        )
        
        page = context.new_page()
        
        # --- HARDENING & STEALTH: Manual Navigator Overrides ---
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => false});
            Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
            Object.defineProperty(navigator, 'languages', {get: () => ['es-419', 'es', 'en-US', 'en']});
        """)
        
        # --- MINIMALIST MODE: Animations only ---
        page.add_init_script("""
            const style = document.createElement('style');
            style.innerHTML = `
                * { transition: none !important; animation: none !important; }
            `;
            document.head.appendChild(style);
        """)
        
        # --- Memory Saver: Block images, fonts, and media ---
        def route_handler(route):
            if route.request.resource_type in ["image", "font", "media"]:
                route.abort()
            else:
                route.continue_()
                
        page.route("**/*", route_handler)
        
        print(f"Navigating to {WHATSAPP_URL}...")
        page.goto(WHATSAPP_URL)
        
        # Wait for the chat list to load (indicator of login)
        print("Waiting for WhatsApp Web to load. If this is your first run, please scan the QR code.")
        
        # --- MULTI-LANGUAGE LOGIN DETECTION ---
        try:
            print("Checking session status (Waiting for dashboard)...")
            # Look for English, Spanish, or universal markers
            page.wait_for_selector('div[aria-label="Chat list"], div[aria-label="Lista de chats"], div[data-testid="search"]', timeout=120000)
            print("Login successful or session restored!")
        except Exception:
            print("\n--- LOGIN REQUIRED ---")
            print(f"Current Page: {page.title()} | URL: {page.url}")
            
            # DIAGNOSTIC: What is actually on the screen?
            try:
                debug_text = page.inner_text("body")[:400].replace("\n", " ")
                print(f"DEBUG: Screen Content: {debug_text}")
            except: 
                pass

            print("Looking for QR code FAST...")
            try:
                # Prioritize 'canvas' as it's the fastest and most stable
                qr_selectors = [
                    'canvas', 
                    'div[data-ref]', 
                    '[data-testid="qrcode-container"]',
                    'div[aria-label="Scan me!"]'
                ]
                
                qr_found = False
                for sel in qr_selectors:
                    try:
                        # Use short timeout per selector to find it quickly
                        page.wait_for_selector(sel, state="visible", timeout=8000)
                        qr_found = True
                        break
                    except:
                        continue

                if not qr_found:
                    raise Exception("QR selectors not found in time.")

                print("⚡ QR CODE IS LIVE! Saving immediately...")
                time.sleep(2) # Reduced from 5s to 2s
                
                qr_path = "qr.png"
                page.screenshot(path=qr_path)
                print(f"!!! DOWNLOAD AND SCAN {qr_path} NOW !!!")
            except Exception as e:
                print(f"Failed to find QR code: {e}")
                print("Saving emergency full page screenshot to 'error_page.png'...")
                page.screenshot(path="error_page.png", full_page=True)
            
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
                'div[data-testid="search-container"] input',
                'div[contenteditable="true"][data-tab="3"]',
                'input[data-tab="3"]',
                'input[placeholder="Search or start a new chat"]',
                'input[aria-label="Search or start a new chat"]',
                'div[aria-label="Search input textbox"]'
            ]

            # --- METHOD A: Playwright Roles (Most Resilient) ---
            try:
                # Try finding by role/placeholder
                search_box = page.get_by_placeholder("Search or start a new chat")
                if not search_box.is_visible():
                    search_box = page.get_by_label("Search input textbox")
                
                if search_box and search_box.is_visible(timeout=3000):
                    print("Found search box via Role/Label.")
                else:
                    search_box = None
            except:
                search_box = None

            # --- METHOD B: Selector Fallbacks ---
            if not search_box:
                for selector in selectors_to_try:
                    try:
                        search_box = page.wait_for_selector(selector, state="visible", timeout=2000)
                        if search_box:
                            print(f"Found search box via selector: {selector}")
                            break
                    except Exception:
                        continue
                
            # --- METHOD C: DOM AUDIT (If all else fails) ---
            if not search_box:
                print("DEBUG: All search selectors failed. Auditing DOM inputs...")
                try:
                    # Find any inputs or contenteditables that might be search boxes
                    inputs = page.query_selector_all("input, div[contenteditable]")
                    for i, inp in enumerate(inputs):
                        placeholder = inp.get_attribute("placeholder") or "None"
                        label = inp.get_attribute("aria-label") or "None"
                        print(f"  Input {i}: Placeholder='{placeholder}', Label='{label}'")
                except: pass
                
                print("CRITICAL: Main search box not found. The WhatsApp Web DOM has changed.")
                continue
                
            # Use fill() instead of type() to save memory on 1GB VM
            search_box.fill(name)
            time.sleep(3) # wait for results to populate
            
            # 2. Click the chat in the search results pane
            print(f"Finding results for: {name}...")
            chat_found = False
            
            # --- Result Method A: Exact Title Match ---
            try:
                # Use a specific locator for the chat title to avoid clicking profile pics
                chat_title = page.locator(f'span[title="{name}"], [aria-label="{name}"]')
                if chat_title.first.is_visible(timeout=5000):
                    chat_title.first.click()
                    chat_found = True
                    print(f"Clicked {name} via Title/Label.")
            except: pass

            # --- Result Method B: Text-Based Match (Robust for Special Chars) ---
            if not chat_found:
                try:
                    # Look for the name anywhere in the sidebar results
                    result = page.get_by_text(name, exact=False).first
                    if result.is_visible(timeout=3000):
                        result.click()
                        chat_found = True
                        print(f"Clicked {name} via Text Match.")
                except: pass

            if not chat_found:
                print(f"Could not find chat in search results for: {name}. Skipping.")
                continue

            # Wait for right pane to load
            time.sleep(1.5)

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
