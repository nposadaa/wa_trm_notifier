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
        
        # --- LOGIN DETECTION & SYNC (Robust Loop) ---
        print("Checking session status (State-Aware Loop)...")
        start_time = time.time()
        # 4 minutes total for initial splash/render transition
        MAX_INITIAL_WAIT = 240 
        session_state = "INITIALIZING"
        
        while time.time() - start_time < MAX_INITIAL_WAIT:
            elapsed = int(time.time() - start_time)
            
            # 1. SUCCESS MARKERS (Chat Pane)
            if page.locator('#pane-side, [data-testid="chat-list-search-filtered"]').first.is_visible():
                print(f"[{elapsed}s] Login successful! Chat pane found.")
                session_state = "LOGGED_IN"
                break
            
            # 2. AUTHENTICATION MARKERS (Logout button)
            # Sometimes the chat pane is slow, but the logo/logout is there
            if page.get_by_text("Log out").or_(page.get_by_text("Cerrar sesión")).first.is_visible():
                print(f"[{elapsed}s] Login confirmed via Logout marker.")
                session_state = "LOGGED_IN"
                break

            # 3. SYNCING MARKERS
            if page.get_by_text("Loading your chats").or_(page.get_by_text("Cargando tus chats")).first.is_visible():
                print(f"[{elapsed}s] Syncing detected... extending wait (up to 5 mins).")
                try:
                    # Give it a long time to finish the data sync
                    page.wait_for_selector('#pane-side', timeout=300000)
                    session_state = "LOGGED_IN"
                    break
                except Exception:
                    print(f"[{elapsed}s] Syncing still in progress or timed out. Re-checking markers...")
            
            # 4. QR CODE MARKERS (Login Required)
            if page.locator('canvas, [data-testid="qrcode-container"]').first.is_visible():
                session_state = "QR_REQUIRED"
                break
            
            # 5. SPLASH SCREEN (VM Lag or Initialization)
            # If we see 'End-to-end encrypted' or 'WhatsApp' title, we are likely on splash
            try:
                screen_content = page.inner_text("body")[:1000]
                if "End-to-end encrypted" in screen_content or "WhatsApp" in screen_content:
                    if session_state != "SPLASH":
                        print(f"[{elapsed}s] Splash screen detected (Logo/Encryption splash). Waiting for JS to render...")
                        session_state = "SPLASH"
            except: pass

            time.sleep(10) # 10s intervals to save e2-micro CPU
            print(f"[{elapsed}s] Still initializing (Current State: {session_state})...")

        # --- FINAL EVALUATION ---
        if session_state == "QR_REQUIRED":
            print("\n--- LOGIN REQUIRED ---")
            print(f"Current Page: {page.title()} | URL: {page.url}")
            
            print("⚡ QR CODE IS LIVE! Saving immediately...")
            try:
                # Give it a tiny bit to breathe
                time.sleep(2)
                qr_path = "qr.png"
                page.screenshot(path=qr_path)
                print(f"!!! DOWNLOAD AND SCAN {qr_path} NOW !!!")
            except Exception as e:
                print(f"Failed to save QR screenshot: {e}")
                page.screenshot(path="error_page.png", full_page=True)
            
            context.close()
            return
            
        elif session_state != "LOGGED_IN":
            print(f"\n--- SESSION TIMEOUT ({session_state}) ---")
            print(f"Reached {MAX_INITIAL_WAIT}s without entering logged-in state.")
            print("Saving diagnostic screenshot to 'error_page.png'...")
            page.screenshot(path="error_page.png", full_page=True)
            context.close()
            return

        print("Session fully stabilized.")

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
            print(f"Finding input box for {name}...")
            chat_box = None
            
            # --- Method A: Role-based (Most Resilient) ---
            try:
                # Try finding by localized role in the #main area
                chat_box = page.locator('#main').get_by_role("textbox", name="Type a message").or_(
                    page.locator('#main').get_by_role("textbox", name="Escribe un mensaje")
                ).first
                
                if chat_box.is_visible(timeout=5000):
                    print("Found chat box via Role.")
                else: chat_box = None
            except: chat_box = None

            # --- Method B: Selector Fallbacks ---
            if not chat_box:
                chat_box_selectors = [
                    'footer div[contenteditable="true"]',
                    '#main div[aria-label="Type a message"]',
                    '#main div[aria-label="Escribe un mensaje"]',
                    'p.selectable-text.copyable-text'
                ]
                for sel in chat_box_selectors:
                    try:
                        chat_box = page.wait_for_selector(sel, state="visible", timeout=2000)
                        if chat_box: 
                            print(f"Found chat box via selector: {sel}")
                            break
                    except: continue

            if not chat_box:
                 print(f"Could not find the chat input box for {name}.")
                 continue
                 
            # 4. Fill message and send
            print(f"Typing message to {name}...")
            chat_box.click() # Ensure focus
            chat_box.fill(message_text)
            time.sleep(1.5) # Let the UI react to the text
            
            # --- Robust Send Method ---
            try:
                # Look for the Send button icon (data-testid="send")
                send_button = page.locator('button:has(span[data-testid="send"]), [data-testid="send"]').first
                if send_button.is_visible(timeout=3000):
                    print("Clicking Send button icon...")
                    send_button.click()
                else:
                    print("Send button icon not visible. Falling back to Enter key...")
                    chat_box.press("Enter")
            except Exception as e:
                print(f"Send button error ({e}). Falling back to Enter key...")
                chat_box.press("Enter")

            print(f"✅ SUCCESS: Sent message to {name}!")
            # 5s wait between recipients to allow server sync
            time.sleep(5) 

        print("\nAll recipients processed. Final delivery buffer (10s)...")
        # CRITICAL: Wait 10s to ensure the WebSocket actually uploads the data before we kill the browser
        time.sleep(10)
        context.close()


if __name__ == "__main__":
    import sys
    # Check for flags
    disco = "--discovery" in sys.argv
    run_broadcaster(message_text="Discovery Test", headless=False, discovery_mode=disco)
