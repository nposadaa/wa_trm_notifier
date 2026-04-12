import os
import time
import json
from playwright.sync_api import sync_playwright
from browser_config import get_browser_context, clean_browser_locks, apply_stealth_overrides
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
    clean_browser_locks()
    with sync_playwright() as p:
        # --- Browser Initialization ---
        context = get_browser_context(p, headless=headless)
        page = context.new_page()
        
        # --- HARDENING & STEALTH: Manual Navigator Overrides ---
        apply_stealth_overrides(page)
        
        # (DEC-014: Resource filtering disabled for stability)

        # --- Console Mirroring (DEC-009) ---
        # Mirrors browser-level errors/warnings to VM console for remote diagnostics
        page.on("console", lambda msg: print(f"[BROWSER-LOG] {msg.type.upper()}: {msg.text}") if msg.type in ["error", "warning"] else None)
        
        print(f"Navigating to {WHATSAPP_URL}...")
        page.goto(WHATSAPP_URL)
        
        # Wait for the chat list to load (indicator of login)
        print("Waiting for WhatsApp Web to load. If this is your first run, please scan the QR code.")
        
        # --- LOGIN DETECTION & SYNC (Stabilized Flow) ---
        print("Checking session status (State-Aware Loop)...")
        start_time = time.time()
        poll_start = time.time()
        # 20 minutes for initial deep sync on first heartbeats
        MAX_INITIAL_WAIT = 1200 
        session_state = "INITIALIZING"
        reload_triggered = False
        last_percentage = -1
        
        while time.time() - start_time < MAX_INITIAL_WAIT:
            elapsed = int(time.time() - start_time)
            
            # Watchdog: If no state change or percentage progress for 5 mins, fail
            if time.time() - poll_start > 300:
                print(f"[{elapsed}s] CRITICAL: No progress for 5 minutes. Timing out.")
                break

            # 0. DISMISS BLOCKING MODALS (Bypass)
            try:
                page.evaluate("""() => {
                    const targets = ['Actualizar', 'Update', 'Cerrar', 'Close', 'Más tarde', 'Later', 'OK'];
                    document.querySelectorAll('button, [role="button"]').forEach(btn => {
                        if (targets.some(t => btn.innerText.includes(t))) btn.click();
                    });
                }""")
            except: pass

            # 1. SUCCESS MARKERS (Search Box or Chat Pane)
            if page.locator('#pane-side, [data-testid="chat-list-search-filtered"], #side [contenteditable="true"]').first.is_visible():
                print(f"[{elapsed}s] Login successful! Chat UI detected.")
                session_state = "LOGGED_IN"
                break
            
            # 3. SYNCING & PROGRESS MARKERS
            screen_content = ""
            try: screen_content = page.locator("body").inner_text()[:2000]
            except: pass

            if "Loading your chats" in screen_content or "Cargando tus chats" in screen_content:
                if session_state != "SYNCING":
                    print(f"[{elapsed}s] Syncing detected... (First run decryption phase).")
                    session_state = "SYNCING"
                
                # Extract percentage to verify progress (e.g., "Loading your chats [19%]")
                import re
                match = re.search(r'\[(\d+)%\]', screen_content)
                if match:
                    current_pct = int(match.group(1))
                    if current_pct > last_percentage:
                        print(f"[{elapsed}s] Sync Progress: {current_pct}% (CPU Decrypting...)")
                        last_percentage = current_pct
                        poll_start = time.time() # Reset watchdog - we have progress!

                # RECOVERY: If stuck at 0% or no % for > 240s, jumpstart
                if elapsed > 240 and not reload_triggered and last_percentage <= 0:
                    print(f"[{elapsed}s] WARNING: Sync hang suspected. Triggering jumpstart reload...")
                    page.reload()
                    reload_triggered = True
                    poll_start = time.time()
                    time.sleep(5)
                    continue

                try:
                    page.wait_for_selector('#pane-side, #side [contenteditable="true"]', timeout=30000)
                    session_state = "LOGGED_IN"
                    break
                except : pass
            
            # 4. QR CODE MARKERS
            if page.locator('canvas, [data-testid="qrcode-container"]').first.is_visible():
                context.close()
                raise RuntimeError("Session Invalidated! (QR Required).")
            
            # 5. SPLASH SCREEN (Initial)
            if "WhatsApp" in screen_content and session_state == "INITIALIZING":
                print(f"[{elapsed}s] Splash detected. Waiting for decryption...")
                session_state = "SPLASH"

            time.sleep(15) 
            print(f"[{elapsed}s] Auth Loop: {session_state}...")

        # --- SETTLING WINDOW (DEC-014) ---
        if session_state == "LOGGED_IN":
            print("Session fully stabilized. Checking for background sync activity...")
            # EXTRA: Wait for the sidebar 'Syncing chats...' message to disappear
            for _ in range(20): # Up to 5 more minutes of grace
                sync_status = page.locator('div:has-text("Syncing chats"), div:has-text("Sincronizando")').first
                if sync_status.is_visible(timeout=1000):
                    status_text = ""
                    try: status_text = sync_status.inner_text().strip()
                    except: pass
                    print(f"  [Syncing] {status_text}...")
                    time.sleep(15)
                else:
                    print("  [Syncing] Sidebar sync message gone. Proceeding.")
                    break
            time.sleep(5)
        else:
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
                time.sleep(1.0) # Increased for stability
                # Type characters with tiny delay to satisfy React listeners on slow VM
                page.keyboard.type(name, delay=70) 
                time.sleep(2.0)
                page.keyboard.press("Enter")
            except Exception as e:
                print(f"Search box keyboard interaction failed: {e}. Trying raw press...")
                page.keyboard.press("Enter")
            
            # 2. Click the chat in the search results pane (Retry Loop)
            print(f"Auditing results for: {name}...")
            chat_found = False
            
            # Give the VM up to 30s for the sidebar to populate (Slow VM Fix)
            for attempt in range(5):
                # --- Result Method A: Exact Title Match ---
                try:
                    chat_title = page.locator(f'span[title="{name}"], [aria-label="{name}"]').first
                    if chat_title.is_visible(timeout=4000):
                        chat_title.click()
                        chat_found = True
                        print(f"SUCCESS: Clicked {name} via Sidebar match ({attempt+1}/5).")
                        break
                except: pass
    
                # --- Result Method B: Flexible Text Match ---
                if not chat_found:
                    try:
                        result = page.get_by_text(name, exact=False).first
                        if result.is_visible(timeout=3000):
                            result.click()
                            chat_found = True
                            print(f"SUCCESS: Clicked {name} via Text fallback ({attempt+1}/5).")
                            break
                    except: pass
                
                if not chat_found:
                    print(f"Attempt {attempt+1}/5: Still searching sidebar...")
                    time.sleep(5)
            
            if not chat_found:
                print(f"CRITICAL: Search failed for '{name}'. Saving search_failed.png")
                page.screenshot(path=f"diag_search_failed_{name.replace('/', '_')}.png")
                continue

            time.sleep(3.0) # Stability buffer

            # 3. Focus the chat input box (bottom bar of right pane)
            print(f"Finding input box for {name}...")
            box_handle = None
            try:
                box_handle = page.wait_for_selector(
                    '#main div[contenteditable="true"], footer div[contenteditable="true"]', 
                    state="visible", 
                    timeout=15000
                )
            except Exception as e:
                print(f"Could not find the chat input box for {name}: {e}")
                continue
                 
            # 4. Type message using keyboard events (DEC-018)
            print(f"Typing message to {name}...")
                
            box_handle.click()
            box_handle.evaluate("el => el.focus()")
            
            # Clear any residual text
            page.keyboard.press("Control+a")
            page.keyboard.press("Backspace")
            time.sleep(0.5)
            
            lines = message_text.split('\n')
            for i, line in enumerate(lines):
                if line:
                    box_handle.type(line, delay=20)
                if i < len(lines) - 1:
                    page.keyboard.down("Shift")
                    page.keyboard.press("Enter")
                    page.keyboard.up("Shift")
                    time.sleep(0.1)
                
            time.sleep(2.0)

            # --- Robust Send Method ---
            try:
                send_button = page.locator('button:has(span[data-testid="send"]), [data-testid="send"]').first
                if send_button.is_visible(timeout=3000):
                    send_button.click()
                else:
                    box_handle.focus()
                    page.keyboard.press("Enter")
            except:
                page.keyboard.press("Enter")

            # --- Empirical Delivery Verification ---
            # We wait longer for the 'Clock' icon to transition to 'Checkmark'
            print(f"Verifying delivery to {name}...")
            delivery_verified = False
            
            # Up to 3 minutes for slow VM to upload the buffer
            for v_sec in range(180):
                # SUCCESS: Found checkmark
                if page.locator('span[data-testid="msg-check"], span[data-testid="msg-dblcheck"]').last.is_visible(timeout=500):
                    print(f"[{v_sec}s] Delivery Confirmed: Checkmark detected.")
                    delivery_verified = True
                    break
                
                # WARNING: In Outbox (Clock)
                if page.locator('span[data-testid="msg-clock"]').last.is_visible(timeout=500):
                    if v_sec % 10 == 0:
                        print(f"[{v_sec}s] Message in Outbox (Clock icon). Waiting for WebSocket upload...")
                
                time.sleep(1)

            if delivery_verified:
                print(f"✅ SUCCESS: Sent message to {name}!")
            else:
                print(f"❌ FAILURE: Message held in Outbox (Clock) or Missing. Saving diag_delivery_failed.png")
                page.screenshot(path=f"diag_delivery_failed_{name.replace('/', '_')}.png")

            time.sleep(5) 

        print("\nAll recipients processed. Finalizing buffer flush (60s)...")
        # EXTENDED: Give the slow VM a full minute to ensure all WebSockets are closed cleanly
        time.sleep(60)
        context.close()


if __name__ == "__main__":
    import sys
    # Check for flags
    disco = "--discovery" in sys.argv
    run_broadcaster(message_text="Discovery Test", headless=False, discovery_mode=disco)
