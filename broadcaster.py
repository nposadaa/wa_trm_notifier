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


def safe_screenshot(page, path, timeout_ms=10000):
    """Take a diagnostic screenshot without crashing if the browser is frozen. (BUG-003)"""
    try:
        page.screenshot(path=path, timeout=timeout_ms)
        print(f"  Diagnostic saved: {path}")
    except Exception as e:
        print(f"  WARNING: Screenshot failed ({e}). Browser may be frozen.")


def connectivity_guard(page, timeout=120):
    """Abort early if WhatsApp Web is in a 'Connecting/Retrying' state. (BUG-001)

    Polls the sidebar for the connectivity banner. If it does not clear
    within `timeout` seconds, raises RuntimeError so main.py can exit(1).
    Version: 1.0.6
    """
    banner_selectors = (
        'div[role="alert"]'
        ', [data-testid="connectivity-banner"]'
        ', div:has-text("Connecting to WhatsApp")'
        ', div:has-text("Retrying")'
        ', div:has-text("Conectando")'
        ', div:has-text("Reintentando")'
        ', span[data-icon="alert-phone-off"]'
        ', span[data-icon="alert-computer-off"]'
    )
    # Quick initial check — if no banner, proceed immediately
    banner = page.locator(banner_selectors).first
    if not banner.is_visible(timeout=8000): # Increased to catch transient flashes
        return

    print("[CONNECTIVITY] ⚠ Banner detected — waiting for WebSocket restore...")
    waited = 0
    backoff = [5, 5, 10, 10, 15, 15]  # ~60s total
    for i, delay in enumerate(backoff):
        time.sleep(delay)
        waited += delay
        banner = page.locator(banner_selectors).first
        if not banner.is_visible(timeout=2000):
            print(f"[CONNECTIVITY] Banner cleared after {waited}s — proceeding.")
            return
        
        # JUMPSTART: If we've waited 30s and still stuck, try a reload (DEC-031)
        if waited >= 30 and i == 3:
            print(f"[CONNECTIVITY] [{waited}s] Still stuck. Attempting page reload to jumpstart connection...")
            page.reload()
            page.wait_for_load_state("networkidle", timeout=30000)
            time.sleep(10) # Post-reload settling

        print(f"[CONNECTIVITY] [{waited}s/{timeout}s] Still retrying...")

    # Timed out — save diag and abort
    safe_screenshot(page, "diag_connectivity_timeout.png")
    raise RuntimeError(
        f"[CONNECTIVITY] WebSocket not restored after {timeout}s. Aborting send."
    )

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

            # 0. DISMISS BLOCKING MODALS & BANNERS (Bypass / DEC-022)
            try:
                # Defensive UI Cleanup: Only target common overlays
                page.evaluate("""() => {
                    const dismiss = (selector, textMatch = null) => {
                        const items = document.querySelectorAll(selector);
                        items.forEach(el => {
                            if (!textMatch || el.innerText.includes(textMatch)) {
                                el.click();
                            }
                        });
                    };
                    // Generic Buttons
                    ['Actualizar', 'Update', 'Cerrar', 'Close', 'Más tarde', 'Later', 'OK'].forEach(t => dismiss('button, [role="button"]', t));
                    
                    // Specific "Notifications are off" banner close button (data-icon is safer)
                    document.querySelectorAll('span[data-icon="x-alt"], span[data-icon="x"]').forEach(icon => {
                        const btn = icon.closest('div[role="button"], button');
                        if (btn) btn.click();
                    });
                }""")
            except Exception as eval_err:
                pass # Non-critical loop stability

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
            safe_screenshot(page, "error_page.png")
            context.close()
            return False

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

        # --- Pre-send connectivity guard (BUG-001) ---
        connectivity_guard(page)
        time.sleep(3)  # Settling pause after guard

        # --- Direct Broadcasting Logic ---
        any_failure = False
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
                safe_screenshot(page, f"diag_search_failed_{name.replace('/', '_')}.png")
                any_failure = True
                continue

            # --- Pre-type connectivity re-verification (BUG-009) ---
            # Connection can drop after the initial guard during search load.
            try:
                connectivity_guard(page, timeout=30)
            except RuntimeError as e:
                print(f"  [Attempt 1/1] Aborting: {e}")
                any_failure = True
                continue

            time.sleep(3.0) # Stability buffer

            # 3. Target the chat input box (Locator-First / DEC-021)
            print(f"Finding input box for {name}...")
            chat_input = page.locator('#main div[contenteditable="true"], footer div[contenteditable="true"]').first
            
            # 4. Type message using keyboard.insert_text (BUG-006 / DEC-024)
            # press_sequentially mangles emoji surrogate pairs.
            # execCommand('insertText') modifies DOM but NOT React/Lexical state.
            # keyboard.insert_text() dispatches proper InputEvent that Lexical recognizes,
            # AND handles emoji/Unicode natively (designed for IME input).
            print(f"Typing message to {name}...")
            interaction_success = False
            
            for attempt in range(2):
                try:
                    # Ensure the box is ready (Increased timeout for VM stability)
                    chat_input.wait_for(state="visible", timeout=60000)
                    
                    # Force Focus via Locator (BUG-006: no stale element_handle)
                    print(f"  [Attempt {attempt+1}/2] Focusing input and clearing buffer...")
                    chat_input.click()
                    time.sleep(0.3)
                    page.keyboard.press("Control+A")
                    page.keyboard.press("Backspace")
                    time.sleep(0.5)
                    
                    # Insert message line-by-line via keyboard.insert_text
                    # This fires proper browser InputEvent (compatible with React/Lexical)
                    lines = message_text.split('\n')
                    for i, line in enumerate(lines):
                        if line:
                            page.keyboard.insert_text(line)
                            time.sleep(0.3)
                        if i < len(lines) - 1:
                            # Shift+Enter for newlines in WhatsApp
                            page.keyboard.press("Shift+Enter")
                            time.sleep(0.1)
                    
                    time.sleep(2.0)

                    # --- Post-typing verification (BUG-006) ---
                    typed_content = ""
                    try:
                        typed_content = chat_input.inner_text().strip()
                    except Exception:
                        pass
                    
                    if not typed_content:
                        print(f"  [Attempt {attempt+1}/2] WARNING: Input box appears empty after typing!")
                        if attempt == 0:
                            print("  Retrying...")
                            safe_screenshot(page, f"diag_empty_input_{name.replace('/', '_')}.png")
                            time.sleep(3)
                            continue
                    else:
                        print(f"  [Attempt {attempt+1}/2] Typing verified: {len(typed_content)} chars in input box.")

                    # --- Robust Send Method ---
                    send_button = page.locator('button:has(span[data-testid="send"]), [data-testid="send"]').first
                    if send_button.is_visible(timeout=5000):
                        send_button.click()
                        print(f"  [Attempt {attempt+1}/2] Send button clicked.")
                    else:
                        page.keyboard.press("Enter")
                        print(f"  [Attempt {attempt+1}/2] Enter pressed (Send button not found).")
                    
                    interaction_success = True
                    break

                except Exception as e:
                    print(f"  [Attempt {attempt+1}/2] Interaction error: {e}")
                    if attempt == 0:
                        print("  Taking diagnostic screenshot and retrying...")
                        safe_screenshot(page, f"diag_retry_{name.replace('/', '_')}.png")
                        time.sleep(5)
            
            if not interaction_success:
                print(f"CRITICAL: Interaction failed for {name} after all retries. Attempting final emergency Enter...")
                page.keyboard.press("Enter")

            # --- Empirical Delivery Verification (BUG-008 Hardening) ---
            print(f"Verifying delivery to {name} (Watching last row for acknowledgment)...")
            delivery_verified = False
            start_verify = time.time()
            
            try:
                # Give the DOM a moment to generate the row after 'Enter'
                time.sleep(3)
                
                # 1. Verify message presence (BUG-010: don't wait for checkmarks if message isn't even in the chat)
                last_row = page.locator('#main div[role="row"]').last
                row_text = ""
                try: row_text = last_row.inner_text()
                except: pass
                
                # Use a snippet of the message to verify it's the right one
                msg_snippet = message_text[:30].strip().replace("*", "")
                if msg_snippet not in row_text:
                    print(f"⚠️ WARNING: Last row text does not match our message. Send might have failed silently.")
                    print(f"  Expected snippet: '{msg_snippet}'")
                    print(f"  Found in row: '{row_text[:50]}...'")
                    # Fallback: check if we are still focused on the input box (means Enter failed)
                    is_focused = page.evaluate('() => document.activeElement === document.querySelector("#main div[contenteditable=\'true\']")')
                    if is_focused:
                        print("  Input box still focused. Emergency re-Enter...")
                        page.keyboard.press("Enter")
                        time.sleep(5)
                        last_row = page.locator('#main div[role="row"]').last
                
                # 2. Wait for checkmark/double-checkmark WITHIN that row specifically
                status_locator = last_row.locator('span[data-testid="msg-check"], span[data-testid="msg-dblcheck"], span[data-icon="msg-check"], span[data-icon="msg-dblcheck"]')
                
                print(f"  [Verification] Waiting for anchored row checkmark...")
                # Poll instead of pure wait to catch "Fail" or "Clock" states earlier
                for _ in range(60): # 5 minutes total (5s intervals)
                    if status_locator.is_visible(timeout=1000):
                        elapsed_verify = int(time.time() - start_verify)
                        print(f"✅ SUCCESS: Delivery Confirmed via anchored row checkmark (Ack took {elapsed_verify}s).")
                        delivery_verified = True
                        break
                    
                    # Check for "Failed to send" (Red circle/exclamation)
                    if last_row.locator('span[data-icon="msg-exclamation"], [data-testid="msg-fail"], .status-error').first.is_visible(timeout=1000):
                        print("❌ FAILURE: Message failed to send (Red exclamation detected).")
                        break
                        
                    # Check for "Clock" (Outbox hang)
                    if last_row.locator('span[data-testid="msg-clock"], span[data-icon="msg-clock"]').is_visible(timeout=1000):
                        # If stuck for > 60s, try a JUMPSTART RELOAD (one time)
                        if time.time() - start_verify > 60:
                            print("⚠️ WARNING: Message stuck in outbox (Clock) for 60s. Attempting session recovery...")
                            page.reload()
                            page.wait_for_load_state("networkidle", timeout=30000)
                            time.sleep(10)
                            # After reload, check if it was actually sent
                            print("  Post-recovery check...")
                            last_row = page.locator('#main div[role="row"]').last
                            if status_locator.is_visible(timeout=10000):
                                print("✅ SUCCESS: Delivery confirmed after recovery reload.")
                                delivery_verified = True
                                break
                    
                    time.sleep(4)

            except Exception as e:
                print(f"❌ FAILURE: Verification engine crashed ({e})")

            if not delivery_verified:
                print(f"❌ FAILURE: Delivery could not be verified for {name}. Saving diag_delivery_failed_{name.replace('/', '_')}.png")
                safe_screenshot(page, f"diag_delivery_failed_{name.replace('/', '_')}.png")
                any_failure = True

            if not delivery_verified:
                print(f"❌ FAILURE: Delivery could not be verified for {name}. Saving diag_delivery_failed_{name.replace('/', '_')}.png")
                safe_screenshot(page, f"diag_delivery_failed_{name.replace('/', '_')}.png")
                any_failure = True

            time.sleep(5)

        print("\nAll recipients processed. Finalizing buffer flush (60s)...")
        # EXTENDED: Give the slow VM a full minute to ensure all WebSockets are closed cleanly
        time.sleep(60)
        context.close()
        return not any_failure


if __name__ == "__main__":
    import sys
    # Check for flags
    disco = "--discovery" in sys.argv
    run_broadcaster(message_text="Discovery Test", headless=False, discovery_mode=disco)
