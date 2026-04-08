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

        # --- Pre-flight: Clear Browser Locks ---
        # This solves the "persistence denied" error on VMs after abnormal exits (pkill)
        # Chromium leaves LevelDB LOCK files that deadlock WhatsApp's IndexedDB on reboot.
        import glob
        try:
            for lock in glob.glob(os.path.join(USER_DATA_DIR, "**", "LOCK"), recursive=True):
                os.remove(lock)
                print(f"Cleaned up stale LevelDB lock: {lock}")
            for singleton in glob.glob(os.path.join(USER_DATA_DIR, "Singleton*")):
                os.remove(singleton)
                print(f"Cleaned up stale Singleton lock: {singleton}")
        except Exception as e:
            print(f"Lock cleanup partial failure: {e}")

        # Launch persistent context with ADVANCED HARDENING
        print(f"Launching hardened browser with session at {USER_DATA_DIR}...")
        context = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=headless,
            user_agent=USER_AGENT,
            viewport={'width': 1024, 'height': 768},
            permissions=['notifications', 'background-sync'],
            # --- Anti-Detection: Locality matching ---
            timezone_id="America/Bogota",
            locale="es-419",
            # --- Memory & OOM flags ---
            args=[
                "--start-maximized",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-gpu",
                "--disable-3d-apis",
                "--disable-webgl",
                "--disable-software-rasterizer",
                "--no-zygote",
                "--js-flags='--max-old-space-size=512'", 
                "--disable-setuid-sandbox",
                "--no-first-run",
                "--disable-background-networking",
                "--disable-web-security",
                "--password-store=basic",
                "--use-mock-keychain",
                "--disable-features=IsolateOrigins,site-per-process",
                "--unlimited-storage"
            ]
        )
        
        page = context.new_page()
        
        # --- HARDENING & STEALTH: Manual Navigator Overrides ---
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => false});
            Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
            Object.defineProperty(navigator, 'languages', {get: () => ['es-419', 'es', 'en-US', 'en']});
        """)
        
        # (DEC-014: Resource filtering disabled for stability)

        # --- Console Mirroring (DEC-009) ---
        # Mirrors browser-level errors/warnings to VM console for remote diagnostics
        page.on("console", lambda msg: print(f"[BROWSER-LOG] {msg.type.upper()}: {msg.text}") if msg.type in ["error", "warning"] else None)
        
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
                if session_state != "QR_REQUIRED":
                    print("⚡ QR CODE IS LIVE!")
                    try:
                        time.sleep(2)
                        page.screenshot(path="qr.png")
                        print("!!! SCAN THE BROWSER QR CODE NOW !!!")
                    except Exception as e: pass
                    session_state = "QR_REQUIRED"
                
                # If we are headless on the cloud, exit immediately to save CPU.
                # If we are local (headless=False), DO NOT BREAK. Let the loop wait for the user!
                if headless:
                    print("Running headless: Cannot wait for manual scan. Exiting early.")
                    break
            
            # 5. SPLASH SCREEN (VM Lag or Initialization)
            # If we see 'End-to-end encrypted' or 'WhatsApp' title, we are likely on splash
            try:
                screen_content = page.inner_text("body")[:1000]
                if "End-to-end encrypted" in screen_content or "WhatsApp" in screen_content:
                    if session_state != "SPLASH" and session_state != "QR_REQUIRED":
                        print(f"[{elapsed}s] Splash screen detected (Logo/Encryption splash). Waiting for JS to render...")
                        session_state = "SPLASH"
            except: pass

            time.sleep(10) # 10s intervals to save e2-micro CPU
            print(f"[{elapsed}s] Still initializing (Current State: {session_state})...")

        # --- SETTLING WINDOW (DEC-014) ---
        if session_state == "LOGGED_IN":
            print("Session fully stabilized. Waiting 5s for React UI to settle...")
            time.sleep(5)
        if session_state == "QR_REQUIRED":
            print("\n--- LOGIN REQUIRED ---")
            print(f"Current Page: {page.title()} | URL: {page.url}")
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
            
            # 1. Focus the main search box (Persistent Structural Locator)
            # We avoid 'get_by_placeholder' because the placeholder vanishes from the DOM 
            # as soon as we type, which breaks Playwright's lazy re-resolution.
            search_box = page.locator('#side div[contenteditable="true"], div[data-tab="3"], div[aria-label="Search input textbox"]').first
            
            try:
                if not search_box.is_visible(timeout=8000):
                    print("CRITICAL: search box not found after 8s. Auditing DOM...")
                    # Fallback check for any input
                    search_box = page.locator('div[contenteditable="true"], input').first
            except Exception as e:
                print(f"Search box detection warning: {e}. Attempting brute force...")
                search_box = page.locator('#side [contenteditable="true"]').first
            
            if not search_box:
                 print("CRITICAL: Final search box locator failed.")
                 continue

                
            # Use keyboard-only trigger (DEC-016) to bypass GPU-desync on clicks
            print(f"Executing keyboard-only search for: {name}...")
            try:
                search_box.focus() 
                # Robust clear using keyboard
                page.keyboard.press("Control+A")
                page.keyboard.press("Backspace")
                time.sleep(0.5)
                # Type characters with tiny delay to satisfy React listeners on slow VM
                page.keyboard.type(name, delay=50) 
                time.sleep(1.0)
                page.keyboard.press("Enter")
            except Exception as e:
                print(f"Search box keyboard interaction failed: {e}. Trying raw press...")
                page.keyboard.press("Enter")
            
            # 2. Click the chat in the search results pane (Retry Loop)
            print(f"Auditing results for: {name}...")
            chat_found = False
            
            # Give the VM up to 15s for the sidebar to populate
            for attempt in range(3):
                # --- Result Method A: Exact Title Match ---
                try:
                    chat_title = page.locator(f'span[title="{name}"], [aria-label="{name}"]').first
                    if chat_title.is_visible(timeout=4000):
                        chat_title.click()
                        chat_found = True
                        print(f"SUCCESS: Clicked {name} via Sidebar match ({attempt+1}/3).")
                        break
                except: pass
    
                # --- Result Method B: Flexible Text Match ---
                if not chat_found:
                    try:
                        result = page.get_by_text(name, exact=False).first
                        if result.is_visible(timeout=2000):
                            result.click()
                            chat_found = True
                            print(f"SUCCESS: Clicked {name} via Text fallback ({attempt+1}/3).")
                            break
                    except: pass
                
                if not chat_found:
                    print(f"Attempt {attempt+1}/3: Result not visible. Auditing current sidebar items...")
                    # DIAGNOSTIC AUDIT: What is actually in the sidebar?
                    try:
                        items = page.query_selector_all('span[title]')
                        titles = [f"'{i.get_attribute('title')}'" for i in items[:5]]
                        print(f"  DEBUG: Visible Sidebar Items: {', '.join(titles)}")
                    except: pass
                    time.sleep(4)
            
            if not chat_found:
                print(f"CRITICAL: Search failed for '{name}'. Saving search_failed.png")
                page.screenshot(path=f"diag_search_failed_{name.replace('/', '_')}.png")
                continue



            # Wait for right pane to load
            time.sleep(1.5)

            # 3. Focus the chat input box (bottom bar of right pane)
            print(f"Finding input box for {name}...")
            
            # --- Robust Unique Locator (Language Agnostic & Stable) ---
            # Instead of relying on aria-labels that Lexical dynamically toggles,
            # we target the contenteditable div in the main window.
            box_handle = None
            try:
                # We use page.wait_for_selector to atomically wait for visibility AND grab the handle in one step.
                # This prevents React from unmounting the element between wait_for() and element_handle()
                box_handle = page.wait_for_selector(
                    '#main div[contenteditable="true"], footer div[contenteditable="true"]', 
                    state="visible", 
                    timeout=15000
                )
                print("Found chat box successfully.")
            except Exception as e:
                print(f"Could not find the chat input box for {name}: {e}")
                continue
                 
            # 4. Type message using keyboard events (DEC-018)
            # CRITICAL: chat_box.fill() bypasses React's synthetic event system.
            # Using press_sequentially on the locator can timeout if React re-renders
            # the aria-label or DOM. Using an element handle + page.keyboard prevents this.
            # Also, newlines (\n) must be typed as Shift+Enter to avoid premature sending.
            print(f"Typing message to {name}...")
                
            # Click and force focus via JS to guarantee caret placement
            box_handle.click()
            box_handle.evaluate("el => el.focus()")
            
            # Force caret into the text box via evaluate just in case it's a Lexical boundary
            try:
                box_handle.evaluate("el => { const selection = window.getSelection(); const range = document.createRange(); range.selectNodeContents(el); selection.removeAllRanges(); selection.addRange(range); }")
            except: pass
            
            # Clear any residual text first using correct OS modifiers
            page.keyboard.press("Control+a")
            page.keyboard.press("Backspace")
            time.sleep(0.3)
            
            # Re-ensure focus right before typing
            box_handle.evaluate("el => el.focus()")
            
            # Type line by line, using Shift+Enter for newlines
            lines = message_text.split('\n')
            for i, line in enumerate(lines):
                if line:
                    # Type chunks targeting the exact DOM element pointer to prevent focus stealing
                    box_handle.type(line, delay=10)
                if i < len(lines) - 1:
                    page.keyboard.down("Shift")
                    page.keyboard.press("Enter")
                    page.keyboard.up("Shift")
                    time.sleep(0.05)
                
            time.sleep(1.5)  # Let React register the typed content

            # --- Robust Send Method (DEC-010 refined) ---
            try:
                # 1. Try Send Button First (should now be visible after keyboard.type)
                send_button = page.locator('button:has(span[data-testid="send"]), [data-testid="send"]').first
                if send_button.is_visible(timeout=5000):
                    print("Clicking Send button icon...")
                    send_button.click()
                else:
                    # 2. Force Focus and Press Enter
                    print("Send button icon not visible. Forcing focus and Enter key...")
                    box_handle.focus()
                    page.keyboard.press("Enter")
            except Exception as e:
                print(f"Initial send attempt failed: {e}. Trying raw Keyboard Enter...")
                page.keyboard.press("Enter")

            # --- Empirical Delivery Verification ---
            # We wait up to 30s to see the 'Sent' checkmark appear (extra buffer for slow VM).
            # This prevents false positives on slow VMs.
            print(f"Verifying delivery to {name}...")
            delivery_verified = False
            
            for v_sec in range(30):
                # SUCCESS: Found a single or double checkmark on the latest message
                if page.locator('span[data-testid="msg-check"], span[data-testid="msg-dblcheck"]').last.is_visible(timeout=500):
                    print(f"[{v_sec}s] Delivery Confirmed: Checkmark detected.")
                    delivery_verified = True
                    break
                
                # WARNING: Message is still in outbox (Clock icon)
                if page.locator('span[data-testid="msg-clock"]').last.is_visible(timeout=500):
                    if v_sec % 5 == 0:
                        print(f"[{v_sec}s] Message still in Outbox (Clock icon)...")
                
                time.sleep(1)

            if delivery_verified:
                print(f"✅ SUCCESS: Sent message to {name}!")
            else:
                print(f"❌ FAILURE: Message to {name} was not confirmed as sent (Checkmark missing).")
                # Save diagnostic screenshot of the conversation
                page.screenshot(path=f"diag_delivery_failed_{name.replace('/', '_')}.png")

            # Additional cooling period
            time.sleep(2) 

        print("\nAll recipients processed. Final delivery buffer (10s)...")
        # CRITICAL: Wait 10s to ensure the WebSocket actually uploads the data before we kill the browser
        time.sleep(10)
        context.close()


if __name__ == "__main__":
    import sys
    # Check for flags
    disco = "--discovery" in sys.argv
    run_broadcaster(message_text="Discovery Test", headless=False, discovery_mode=disco)
