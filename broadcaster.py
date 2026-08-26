import os
import time
import json
import re
import logging
from datetime import datetime
from playwright.sync_api import sync_playwright
from browser_config import get_browser_context, clean_browser_locks, apply_stealth_overrides
from dotenv import load_dotenv

logger = logging.getLogger("trm_notifier.broadcaster")


def is_recoverable_browser_error(error):
    """Return True when Playwright errors indicate the browser/page/context died mid-session."""
    if error is None:
        return False

    text = str(error).lower()
    patterns = [
        "target page, context or browser has been closed",
        "target closed",
        "execution context was destroyed",
        "browser has been closed",
        "context has been closed",
        "page has been closed",
        "execution context was destroyed",
    ]
    return any(pattern in text for pattern in patterns)


def ensure_page_alive(page):
    """Probe the page and return False if the underlying browser context is already dead."""
    try:
        if page.is_closed():
            print("[RECOVERY] Page object is already closed.")
            return False
        try:
            if page.context.is_closed():
                print("[RECOVERY] Browser context is already closed.")
                return False
        except Exception:
            pass

        page.evaluate("() => document.readyState")
        return True
    except Exception as exc:
        if is_recoverable_browser_error(exc):
            print(f"[RECOVERY] Browser page became unusable: {exc}")
            return False
        print(f"[RECOVERY] Browser page probe failed: {exc}")
        return False


def chat_name_matches_target(candidate, target):
    """Return True when a visible chat label is equivalent to the requested recipient name."""
    if not candidate or not target:
        return False

    def normalize(text):
        value = text.lower().strip()
        value = value.replace("&", " and ")
        value = re.sub(r"[^a-z0-9]+", " ", value)
        return re.sub(r"\s+", " ", value).strip()

    return normalize(candidate) == normalize(target)


# Redefine print to route to logger
def print(*args, **kwargs):
    message = " ".join(str(arg) for arg in args).strip()
    if message:
        msg_upper = message.upper()
        if "CRITICAL" in msg_upper or "❌" in message or "FAILED" in msg_upper or "FAILURE" in msg_upper:
            logger.error(message)
        elif "WARNING" in msg_upper or "⚠️" in message:
            logger.warning(message)
        else:
            logger.info(message)

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


def safe_reload(page, timeout_ms=60000):
    """Safely reload the page, using a higher timeout, waiting for DOMContentLoaded, and catching errors. (BUG-038)"""
    try:
        print(f"  [Reload] Reloading page (timeout={timeout_ms}ms, wait=domcontentloaded)...")
        page.reload(timeout=timeout_ms, wait_until="domcontentloaded")
        time.sleep(5)  # Post-reload settling
    except Exception as e:
        print(f"  [Reload] WARNING: Reload encountered timeout/error ({e}). Proceeding anyway.")


def find_search_box(page):
    """Locate the WhatsApp chat-search input across current UI variants."""
    selectors = [
        'input[aria-label="Search or start a new chat"]',
        'input[placeholder="Search or start a new chat"]',
        'div[role="textbox"][aria-label="Search or start a new chat"]',
        'div[role="textbox"][aria-label*="Search"]',
        'div[aria-label="Search input textbox"]',
        '#side div[contenteditable="true"]',
        'div[contenteditable="true"]',
        'input[type="text"]',
    ]

    for selector in selectors:
        try:
            locator = page.locator(selector).first
            if locator.count() > 0 and locator.is_visible(timeout=2000):
                return locator
        except Exception:
            continue

    return page.locator('input, div[contenteditable="true"]').first


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
            safe_reload(page)
            try:
                page.wait_for_load_state("networkidle", timeout=15000)
            except Exception as e:
                print(f"[CONNECTIVITY] wait_for_load_state timed out/failed ({e}). Continuing.")

        print(f"[CONNECTIVITY] [{waited}s/{timeout}s] Still retrying...")

    # Timed out — save diag and abort
    safe_screenshot(page, "diag_connectivity_timeout.png")
    raise RuntimeError(
        f"[CONNECTIVITY] WebSocket not restored after {timeout}s. Aborting send."
    )

def dismiss_blocking_modals(page):
    """Dismisses blocking modals and banners. (BUG-042)"""
    try:
        page.keyboard.press("Escape")
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
            
            // Look for aria-label="Close" or aria-label="Cerrar"
            document.querySelectorAll('button[aria-label="Close"], button[aria-label="Cerrar"], div[aria-label="Close"], div[aria-label="Cerrar"]').forEach(btn => btn.click());
        }""")
    except Exception as e:
        print(f"  [Modal Dismiss] Failed: {e}")

def run_broadcaster(message_text="", headless=False, discovery_mode=False):
    """
    Launches WhatsApp Web with a persistent session.
    If discovery_mode is True, it will print the names of available chats.
    Otherwise, it loops through recipients, finds their chat, and sends `message_text`.
    """
    needs_maintenance = False
    deep_cleaned = clean_browser_locks()
    with sync_playwright() as p:
        def create_browser_session():
            context = get_browser_context(p, headless=headless)
            page = context.new_page()

            # --- HARDENING & STEALTH: Manual Navigator Overrides ---
            apply_stealth_overrides(page)

            # --- Console Mirroring (DEC-009) ---
            # Mirrors browser-level errors/warnings to VM console for remote diagnostics
            page.on("console", lambda msg: print(f"[BROWSER-LOG] {msg.type.upper()}: {msg.text}") if msg.type in ["error", "warning"] else None)
            page.on("close", lambda: print("[RECOVERY] Page close event fired."))
            try:
                page.on("crash", lambda: print("[RECOVERY] Page crash event fired."))
            except Exception:
                pass

            return context, page

        # --- Browser Initialization ---
        context, page = create_browser_session()

        print(f"Navigating to {WHATSAPP_URL}...")

        try:
            page.goto(WHATSAPP_URL, timeout=60000, wait_until="domcontentloaded")
        except Exception as e:
            print(f"WARNING: Initial page.goto encountered error ({e}). Continuing anyway.")
        
        # Wait for the chat list to load (indicator of login)
        print("Waiting for WhatsApp Web to load. If this is your first run, please scan the QR code.")
        
        # --- LOGIN DETECTION & SYNC (Stabilized Flow) ---
        print("Checking session status (State-Aware Loop)...")
        start_time = time.time()
        poll_start = time.time()
        # 20 minutes for initial deep sync on first heartbeats
        MAX_INITIAL_WAIT = 1800 # 30 minutes for deep sync on throttled VM cold-boots
        session_state = "INITIALIZING"
        reload_triggered = False
        last_percentage = -1
        recovery_attempts = 0
        
        while time.time() - start_time < MAX_INITIAL_WAIT:
            elapsed = int(time.time() - start_time)

            if not ensure_page_alive(page):
                if recovery_attempts >= 2:
                    print("[RECOVERY] Browser session died repeatedly during auth loop. Marking as session failure.")
                    context.close()
                    return False, True

                recovery_attempts += 1
                print(f"[RECOVERY] Browser session died during auth loop. Restarting session ({recovery_attempts}/2)...")
                try:
                    context.close()
                except Exception as close_err:
                    print(f"[RECOVERY] Failed to close dead context: {close_err}")
                context, page = create_browser_session()
                try:
                    page.goto(WHATSAPP_URL, timeout=60000, wait_until="domcontentloaded")
                except Exception as nav_err:
                    print(f"[RECOVERY] Failed to navigate after restart: {nav_err}")
                continue
            
            # Watchdog: If no state change or percentage progress for 5 mins, reload and reset (BUG-041)
            if time.time() - poll_start > 300:
                print(f"[{elapsed}s] WARNING: No progress or state change for 5 minutes. Triggering recovery reload...")
                safe_reload(page)
                poll_start = time.time()
                continue

            # 0. DISMISS BLOCKING MODALS & BANNERS (Bypass / DEC-022)
            if not ensure_page_alive(page):
                continue
            dismiss_blocking_modals(page)

            # 1. SUCCESS MARKERS (Search Box or Chat Pane)
            try:
                if page.locator('#pane-side, [data-testid="chat-list-search-filtered"], #side [contenteditable="true"]').first.is_visible():
                    print(f"[{elapsed}s] Login successful! Chat UI detected.")
                    session_state = "LOGGED_IN"
                    break
            except Exception as detect_err:
                if not ensure_page_alive(page):
                    continue
                print(f"[{elapsed}s] Login detection check failed: {detect_err}")
            
            # 3. SYNCING & PROGRESS MARKERS
            screen_content = ""
            try: screen_content = page.locator("body").inner_text()[:2000]
            except: pass

            if any(term in screen_content for term in ["Loading your chats", "Cargando tus chats", "Sincronizando", "Organizando", "Loading...", "Cargando..."]):
                if session_state != "SYNCING":
                    print(f"[{elapsed}s] Syncing/Loading detected... (CPU-intensive decryption phase).")
                    session_state = "SYNCING"
                
                # Extract percentage to verify progress (e.g., "Loading your chats [19%]")
                match = re.search(r'\[(\d+)%\]', screen_content)
                if match:
                    current_pct = int(match.group(1))
                    if current_pct > last_percentage:
                        print(f"[{elapsed}s] Sync Progress: {current_pct}% (Decrypting...)")
                        last_percentage = current_pct
                        poll_start = time.time() # Reset watchdog - we have progress!
                    elif current_pct == last_percentage and (time.time() - poll_start) > 300:
                         # Stuck at the same percentage for 5 minutes
                         print(f"[{elapsed}s] WARNING: Sync percentage stuck at {current_pct}%. Triggering recovery...")
                         safe_reload(page)
                         poll_start = time.time()
                         continue

                # RECOVERY: If stuck at 0% or no % for > 240s, jumpstart
                if elapsed > 240 and not reload_triggered and last_percentage <= 0:
                    print(f"[{elapsed}s] WARNING: Sync hang suspected. Triggering jumpstart reload...")
                    safe_reload(page)
                    reload_triggered = True
                    poll_start = time.time()
                    time.sleep(5)
                    continue

                try:
                    page.wait_for_selector('#pane-side, #side [contenteditable="true"]', timeout=30000)
                    session_state = "LOGGED_IN"
                    break
                except : pass
            
            # --- FINAL ATTEMPT: If near timeout, try one last reload ---
            if elapsed > (MAX_INITIAL_WAIT - 60) and not reload_triggered:
                print(f"[{elapsed}s] Near timeout! Final emergency reload...")
                safe_reload(page)
                reload_triggered = True
            
            # 4. QR CODE MARKERS
            try:
                if page.locator('canvas, [data-testid="qrcode-container"]').first.is_visible():
                    context.close()
                    raise RuntimeError("Session Invalidated! (QR Required).")
            except Exception as qr_err:
                if not ensure_page_alive(page):
                    continue
                if "qrcode-container" not in str(qr_err):
                    print(f"[{elapsed}s] QR detection check failed: {qr_err}")
            
            # 5. SPLASH SCREEN (Initial)
            if "WhatsApp" in screen_content and session_state == "INITIALIZING":
                print(f"[{elapsed}s] Splash detected. Waiting for decryption...")
                session_state = "SPLASH"

            time.sleep(15) 
            print(f"[{elapsed}s] Auth Loop: {session_state}...")

        # --- SETTLING WINDOW (DEC-014) ---
        if session_state == "LOGGED_IN":
            print("Session fully stabilized. Checking for background sync activity...")
            
            # If a deep clean occurred, wait for the chat list to populate.
            # WhatsApp Web under deep clean has to download and index chats.
            if deep_cleaned:
                print("[Deep Clean Recovery] Deep clean was performed. Waiting for chat list to populate...")
                # Wait for up to 120 seconds (2 minutes) to allow initial indexing.
                # During this time, we poll for the number of chats to be > 5.
                start_settle = time.time()
                while time.time() - start_settle < 120:
                    try:
                        chat_count = page.locator('#pane-side div[role="row"], #pane-side div[role="listitem"], #pane-side div[data-testid="list-item"]').count()
                        print(f"  [Deep Clean Recovery] Found {chat_count} chat rows in sidebar.")
                        if chat_count > 5:
                            if time.time() - start_settle > 30:
                                print("  [Deep Clean Recovery] Sidebar populated with chats. Proceeding.")
                                break
                    except Exception as e:
                        print(f"  [Deep Clean Recovery] Error checking sidebar rows: {e}")
                    time.sleep(10)
                else:
                    print("  [Deep Clean Recovery] Settle window completed. Proceeding to search.")

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
            safe_screenshot(page, f"error_page_{datetime.now().strftime('%H%M')}.png")
            context.close()
            return False, True

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
            return True, False

        if not message_text:
            print("CRITICAL: message_text is empty. Nothing to broadcast.")
            context.close()
            return False, False

        if not os.path.exists(RECIPIENTS_FILE):
             print(f"Error: {RECIPIENTS_FILE} not found.")
             context.close()
             return False, False
             
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
            
            # Dismiss any late-appearing modals (BUG-042)
            dismiss_blocking_modals(page)
            time.sleep(1)
            
            # 1. Focus the main search box (Persistent Structural Locator)
            search_box = find_search_box(page)
            try:
                if search_box.count() == 0 or not search_box.is_visible(timeout=8000):
                    print("CRITICAL: search box not found after 8s. Auditing DOM...")
                    search_box = page.locator('input, div[contenteditable="true"]').first
            except Exception as e:
                print(f"Search box detection warning: {e}. Attempting brute force...")
                search_box = page.locator('input, div[contenteditable="true"]').first

            if search_box.count() == 0:
                print("CRITICAL: Final search box locator failed.")
                continue

            # Use keyboard-only trigger (DEC-016) to bypass GPU-desync on clicks
            print(f"Executing keyboard-only search for: {name}...")
            try:
                search_box.click()
                search_box.focus()
                page.keyboard.press("Control+A")
                page.keyboard.press("Backspace")
                time.sleep(0.5)
                search_box.type(name, delay=70, timeout=10000)
                time.sleep(2.0)
                page.keyboard.press("Enter")
            except Exception as e:
                print(f"Search box keyboard interaction failed: {e}. Trying raw press...")
                page.keyboard.press("Enter")
            
            # 2. Click the chat in the search results pane (Retry Loop)
            print(f"Auditing results for: {name}...")
            chat_found = False

            # Give the VM up to 30s (or 60s if deep_cleaned) for the sidebar to populate (Slow VM Fix)
            max_search_attempts = 10 if deep_cleaned else 5
            for attempt in range(max_search_attempts):
                try:
                    chat_candidates = page.locator('#pane-side span[title], #pane-side [aria-label], #pane-side [title]').all()
                    for chat in chat_candidates:
                        try:
                            candidate_text = chat.get_attribute('title') or chat.get_attribute('aria-label') or chat.inner_text()
                        except Exception:
                            continue
                        if chat_name_matches_target(candidate_text, name):
                            try:
                                chat.click()
                                chat_found = True
                                print(f"SUCCESS: Clicked {name} via normalized sidebar match ({attempt+1}/{max_search_attempts}).")
                                break
                            except Exception as exc:
                                print(f"  [Search] Click attempt failed for {name}: {exc}")
                                continue
                    if chat_found:
                        break
                except Exception as exc:
                    print(f"  [Search] Sidebar scan warning: {exc}")

                if not chat_found:
                    try:
                        visible_chats = page.locator('#pane-side div[role="row"], #pane-side div[role="listitem"], #pane-side div[data-testid="list-item"]').count()
                        print(f"  [Search Diagnostic] Current visible chat rows in sidebar: {visible_chats}")
                    except Exception as e:
                        print(f"  [Search Diagnostic] Error counting sidebar rows: {e}")
                    print(f"Attempt {attempt+1}/{max_search_attempts}: Still searching sidebar...")
                    time.sleep(5)
            
            if not chat_found:
                screenshot_name = f"diag_search_failed_{name.replace('/', '_')}_{datetime.now().strftime('%H%M')}.png"
                print(f"CRITICAL: Search failed for '{name}'. Saving {screenshot_name}")
                safe_screenshot(page, screenshot_name)
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
            
            # --- Anti-duplicate Deduplication Guard (BUG-020/BUG-039 Hardening) ---
            # If the last row in the chat already contains our message snippet, we skip sending
            # to prevent duplicate posts during retry / fallback / verification-recovery runs.
            msg_snippet = re.sub(r'\s+', ' ', re.sub(r'[^\x00-\x7F]+', '', message_text[:100])).strip().replace("*", "")
            msg_snippet_norm = re.sub(r'\s+', ' ', msg_snippet).strip()
            
            already_sent = False
            try:
                # Ensure DOM is ready and load last row
                last_row = page.locator('#main div[role="row"], #main div[data-id]').last
                if last_row.count() > 0:
                    last_row_text = last_row.inner_text()
                    last_row_norm = re.sub(r'\s+', ' ', last_row_text).strip()
                    if msg_snippet_norm and msg_snippet_norm in last_row_norm:
                        # Ensure the matching row has a confirmed delivery checkmark indicator
                        has_checkmark = False
                        try:
                            has_checkmark = last_row.locator(
                                'span[data-icon="msg-check"], span[data-icon="msg-dblcheck"], span[data-icon="msg-dblcheck-ack"],'
                                ' span[data-icon="status-check"], span[data-icon="status-dblcheck"],'
                                ' span[data-testid="msg-check"], span[data-testid="msg-dblcheck"],'
                                ' span[data-icon*="check"],'
                                ' [aria-label="Delivered"], [aria-label="Sent"], [aria-label="Read"],'
                                ' [aria-label="Entregado"], [aria-label="Leído"], [aria-label="Enviado"]'
                            ).first.is_visible(timeout=2000)
                        except Exception as check_err:
                            print(f"  [Deduplication Checkmark Error] {check_err}")

                        if has_checkmark:
                            print(f"  [Deduplication] Last message in chat matches snippet AND has confirmed checkmark. Skipping send.")
                            already_sent = True
                        else:
                            print(f"  [Deduplication] Message snippet matches last row BUT no checkmark detected (stuck in outbox/pending). Resending...")
                            already_sent = False
            except Exception as e:
                print(f"  [Deduplication Warning] Failed to check last message for duplication: {e}")

            if already_sent:
                print(f"✅ SUCCESS: Deduplication activated — delivery confirmed via pre-existing last row.")
                time.sleep(5)
                continue

            # 4. Type message using keyboard.insert_text (BUG-006 / DEC-024)
            # press_sequentially mangles emoji surrogate pairs.
            # execCommand('insertText') modifies DOM but NOT React/Lexical state.
            # keyboard.insert_text() dispatches proper InputEvent that Lexical recognizes,
            # AND handles emoji/Unicode natively (designed for IME input).
            print(f"Typing message to {name}...")
            interaction_success = False
            pre_send_row_count = None
            pre_send_last_row_text = ""
            
            for attempt in range(2):
                try:
                    # Ensure the box is ready (Increased timeout for VM stability)
                    chat_input.wait_for(state="visible", timeout=60000)
                    
                    # --- Robust Clear Loop (BUG-020) ---
                    print(f"  [Attempt {attempt+1}/2] Clearing composer...")
                    chat_input.click()
                    time.sleep(0.5)
                    for _ in range(3):
                        page.keyboard.press("Control+A")
                        page.keyboard.press("Backspace")
                        time.sleep(0.5)
                        if not chat_input.inner_text().strip():
                            break
                    else:
                         # Brute force fallback via page.evaluate
                         page.evaluate("(el) => { if(el) el.innerText = ''; }", chat_input.element_handle())
                    
                    # Insert message line-by-line via keyboard.insert_text
                    print(f"  [Attempt {attempt+1}/2] Typing message...")
                    lines = message_text.split('\n')
                    for i, line in enumerate(lines):
                        if line:
                            page.keyboard.insert_text(line)
                            time.sleep(0.3)
                        if i < len(lines) - 1:
                            page.keyboard.press("Shift+Enter")
                            time.sleep(0.1)
                    
                    # React DOM Trigger
                    page.keyboard.type(" ", delay=50)
                    time.sleep(0.5)
                    page.keyboard.press("Backspace")
                    time.sleep(2.0)

                    # --- Post-typing verification ---
                    typed_content = ""
                    try: typed_content = chat_input.inner_text().strip()
                    except: pass
                    
                    if not typed_content:
                        print(f"  [Attempt {attempt+1}/2] WARNING: Input box appears empty after typing!")
                        screenshot_name = f"diag_empty_input_{name.replace('/', '_')}_{datetime.now().strftime('%H%M')}.png"
                        safe_screenshot(page, screenshot_name)
                        if attempt == 0:
                            print("  Retrying...")
                            time.sleep(3)
                            continue
                    else:
                        print(f"  [Attempt {attempt+1}/2] Typing verified: {len(typed_content)} chars.")

                    pre_send_row_count = page.locator('#main div[role="row"], #main div[data-id]').count()
                    try:
                        pre_send_last_row = page.locator('#main div[role="row"], #main div[data-id]').last
                        if pre_send_last_row.count() > 0:
                            pre_send_last_row_text = pre_send_last_row.inner_text()
                    except Exception as last_row_err:
                        print(f"  [Warning] Failed to capture pre-send last row text: {last_row_err}")
                    
                    send_button = page.locator('span[data-icon="send"], button:has(span[data-testid="send"]), [data-testid="send"], button[aria-label="Send"], button[aria-label="Enviar"]').first
                    try:
                        if send_button.is_visible(timeout=5000):
                            send_button.click(timeout=5000, no_wait_after=True)
                            print(f"  [Attempt {attempt+1}/2] Send button clicked.")
                        else:
                            page.keyboard.press("Enter")
                            print(f"  [Attempt {attempt+1}/2] Enter pressed.")
                    except Exception as click_err:
                        print(f"  [Attempt {attempt+1}/2] Send button click error ({click_err}). Falling back to Enter key...")
                        try:
                            chat_input.focus()
                        except Exception:
                            pass
                        page.keyboard.press("Enter")
                    
                    time.sleep(2)
                    
                    # --- Post-send: Verify input emptied ---
                    post_send_content = ""
                    try: post_send_content = chat_input.inner_text().strip()
                    except: pass
                    
                    if post_send_content:
                        print(f"  [Attempt {attempt+1}/2] ⚠️ Input NOT empty after send!")
                        for send_retry in range(3):
                            chat_input.click()
                            time.sleep(0.5)
                            page.keyboard.type(" ", delay=100)
                            time.sleep(0.5)
                            page.keyboard.press("Backspace")
                            time.sleep(1.0)
                            send_btn = page.locator('span[data-icon="send"], [data-testid="send"], button[aria-label="Send"], button[aria-label="Enviar"]').first
                            if send_btn.is_visible(timeout=3000):
                                send_btn.click()
                            else:
                                page.keyboard.press("Enter")
                            time.sleep(2)
                            if not chat_input.inner_text().strip():
                                print(f"    Send retry {send_retry+1}/3: ✅ Success.")
                                break
                        else:
                            print(f"  [Attempt {attempt+1}/2] ❌ All send retries exhausted.")
                            screenshot_name = f"diag_send_stuck_{name.replace('/', '_')}_{datetime.now().strftime('%H%M')}.png"
                            safe_screenshot(page, screenshot_name)
                            if attempt == 0: continue
                    else:
                        print(f"  [Attempt {attempt+1}/2] ✅ Input emptied — message dispatched.")
                    
                    interaction_success = True
                    break

                except Exception as e:
                    print(f"  [Attempt {attempt+1}/2] Interaction error: {e}")
                    if attempt == 0:
                        screenshot_name = f"diag_retry_{name.replace('/', '_')}_{datetime.now().strftime('%H%M')}.png"
                        safe_screenshot(page, screenshot_name)
                        time.sleep(5)
            
            if not interaction_success:
                print(f"CRITICAL: Interaction failed for {name} after all retries. Attempting final emergency Enter...")
                page.keyboard.press("Enter")

            # --- Empirical Delivery Verification (BUG-008 Hardening) ---
            print(f"Verifying delivery to {name} (Watching last row for acknowledgment)...")
            delivery_verified = False
            message_confirmed_in_dom = False
            is_stuck_in_outbox = False
            start_verify = time.time()
            
            try:
                # 1. Anti-false-positive: Verify NEW row appeared (BUG-012)
                # Poll for up to 15 seconds to allow slow VMs to render the new row or update text (BUG-025/BUG-035 virtualization-robust)
                row_added = False
                post_send_row_count = pre_send_row_count
                
                # Strip non-ASCII (emojis) and normalize whitespace for robust matching (BUG-011/BUG-012)
                msg_snippet = re.sub(r'\s+', ' ', re.sub(r'[^\x00-\x7F]+', '', message_text[:100])).strip().replace("*", "")
                msg_snippet_norm = re.sub(r'\s+', ' ', msg_snippet).strip()
                
                for verify_attempt in range(10): # Increased to 10 iterations (30s max) for VM rendering
                    post_send_row_count = page.locator('#main div[role="row"], #main div[data-id]').count()
                    
                    # Handle DOM virtualization: if row count drops to 0, scroll to re-render (BUG-048)
                    if post_send_row_count == 0:
                        print(f"  [Verification] Row count is 0 — DOM virtualization detected. Scrolling to bottom...")
                        try:
                            page.keyboard.press("End")
                        except Exception:
                            pass
                        time.sleep(3)
                        continue
                    
                    # Fetch current last row text
                    last_row = page.locator('#main div[role="row"], #main div[data-id]').last
                    last_row_text = ""
                    if last_row.count() > 0:
                        try: last_row_text = last_row.inner_text()
                        except: pass
                    
                    # Normalize whitespace for comparison
                    last_row_norm = re.sub(r'\s+', ' ', last_row_text).strip()
                    pre_row_norm = re.sub(r'\s+', ' ', pre_send_last_row_text).strip()
                    
                    # A new row is successfully added if:
                    # A. The DOM row count increased (direct append without virtualization unmounting)
                    # B. OR the last row text changed and now contains our message snippet (virtualized recycle occurred)
                    # C. OR the last row text contains our snippet and pre-send text was empty
                    if (pre_send_row_count is not None and post_send_row_count > pre_send_row_count) or \
                       (last_row_norm != pre_row_norm and msg_snippet_norm in last_row_norm) or \
                       (not pre_row_norm and msg_snippet_norm in last_row_norm):
                        row_added = True
                        break
                    print(f"  [Verification] Waiting for new row count or text change ({verify_attempt+1}/10)...")
                    time.sleep(3)
                
                print(f"  [Row Count] Before send: {pre_send_row_count}, After send: {post_send_row_count}")
                
                if not row_added:
                    if interaction_success:
                        print(f"  ⚠️ WARNING: Row verification inconclusive (before={pre_send_row_count}, after={post_send_row_count}). Composer emptied — proceeding with text check.")
                    else:
                        print(f"  ❌ CRITICAL: No new message row appeared in DOM or text did not update after 30s.")
                        print(f"  Send CONFIRMED FAILED. Aborting verification to prevent false-positive.")
                        raise RuntimeError(f"Send failed: no new row/text change (before={pre_send_row_count}, after={post_send_row_count})")
                
                # Fetch final last row for checkmark verification
                last_row = page.locator('#main div[role="row"], #main div[data-id]').last
                row_text = ""
                try: row_text = last_row.inner_text()
                except: pass
                
                row_text_check = re.sub(r'\s+', ' ', row_text).strip()
                if msg_snippet and msg_snippet not in row_text_check:
                    print(f"⚠️ WARNING: Last row text does not match our message.")
                    print(f"  Expected snippet: '{msg_snippet}'")
                    print(f"  Found in row: '{row_text_check[:80]}...'")
                    raise RuntimeError(f"Row text mismatch: new row doesn't contain our message")
                # 2. Verify message presence and wait for checkmark
                print(f"  [Verification] Waiting for message to appear in DOM...")
                
                # Poll the last row text for up to 30s to allow slow VMs to render the new message
                row_matched = False
                msg_snippet_norm = re.sub(r'\s+', ' ', msg_snippet).strip()
                
                for _ in range(10): # 10 * 3s = 30 seconds max
                    last_row = page.locator('#main div[role="row"], #main div[data-id]').last
                    final_row_text = ""
                    try: final_row_text = last_row.inner_text()
                    except: pass
                    
                    row_text_norm = re.sub(r'\s+', ' ', final_row_text).strip()
                    if msg_snippet_norm and msg_snippet_norm in row_text_norm:
                        row_matched = True
                        message_confirmed_in_dom = True
                        break
                    
                    time.sleep(3)
                
                if not row_matched:
                    raise RuntimeError(f"Row text mismatch after 30s. Expected: '{msg_snippet_norm}' Found: '{row_text_norm[:80]}'")
                
                print(f"  [Verification] Message matched in DOM. Waiting for anchored row checkmark...")
                # Poll instead of pure wait to catch "Fail" or "Clock" states earlier
                verify_deadline = time.time() + 120 # 2 minutes hard limit (BUG-047/BUG-048)
                consecutive_drifts = 0
                is_stuck_in_outbox = False
                reload_attempted = False
                
                while time.time() < verify_deadline:
                    # Find our message row (robust to virtualization/drifts)
                    target_row = None
                    last_row = page.locator('#main div[role="row"], #main div[data-id]').last
                    
                    # 1. Try last row first (most common)
                    current_row_text = ""
                    try: current_row_text = last_row.inner_text()
                    except: pass
                    row_text_norm = re.sub(r'\s+', ' ', current_row_text).strip()
                    
                    if msg_snippet_norm in row_text_norm:
                        target_row = last_row
                        consecutive_drifts = 0
                    else:
                        # 2. Fall back to scanning all rows in reverse if last row drifted
                        try:
                            all_rows = page.locator('#main div[role="row"], #main div[data-id]').all()
                            for r in reversed(all_rows):
                                try:
                                    r_text = re.sub(r'\s+', ' ', r.inner_text()).strip()
                                    if msg_snippet_norm in r_text:
                                        target_row = r
                                        break
                                except:
                                    pass
                        except Exception as e_scan:
                            print(f"  [Verification] Error scanning chat rows: {e_scan}")
                        
                        if target_row:
                            consecutive_drifts = 0
                        else:
                            consecutive_drifts += 1
                            print(f"  [Verification] ⚠️ Last row text drifted (consecutive drifts: {consecutive_drifts}). Continuing poll...")
                            if consecutive_drifts >= 5:
                                print("  [Verification] ⚠️ Scrolling to bottom to force DOM re-render...")
                                try:
                                    page.keyboard.press("End")
                                except Exception as se:
                                    print(f"  [Verification] Scroll error: {se}")
                                consecutive_drifts = 0
                            time.sleep(5)
                            continue
                    
                    # Create status locator dynamically on the identified row
                    status_locator = target_row.locator(
                        'span[data-testid="msg-check"], span[data-testid="msg-dblcheck"],'
                        ' span[data-icon="msg-check"], span[data-icon="msg-dblcheck"],'
                        ' span[data-icon*="check"],'
                        ' [aria-label="Delivered"], [aria-label="Read"], [aria-label="Sent"],'
                        ' [aria-label="Entregado"], [aria-label="Leído"], [aria-label="Enviado"]'
                    )
                    
                    if status_locator.is_visible(timeout=1000):
                        elapsed_verify = int(time.time() - start_verify)
                        print(f"✅ SUCCESS: Delivery Confirmed via anchored row checkmark (Ack took {elapsed_verify}s).")
                        delivery_verified = True
                        is_stuck_in_outbox = False
                        break
                    
                    # Check for "Failed to send" (Red circle/exclamation)
                    if target_row.locator('span[data-icon="msg-exclamation"], [data-testid="msg-fail"], .status-error').first.is_visible(timeout=1000):
                        print("❌ FAILURE: Message failed to send (Red exclamation detected).")
                        is_stuck_in_outbox = False
                        break
                        
                    # Check for "Clock" (Outbox hang / Pending state)
                    clock_locator = target_row.locator(
                        'span[data-testid="msg-clock"], span[data-icon="msg-clock"],'
                        ' span[data-testid="msg-time"], span[data-icon="msg-time"],'
                        ' span[data-testid="time"], span[data-icon="time"],'
                        ' [aria-label*="Pending"], [aria-label*="Pendiente"], [aria-label*="Clock"]'
                    )
                    if clock_locator.is_visible(timeout=1000):
                        is_stuck_in_outbox = True
                        print(f"  [Verification] ⏳ Outbox pending state detected (Clock icon visible).")
                        # If stuck for > 60s, try a JUMPSTART RELOAD (one time)
                        if time.time() - start_verify > 60 and not reload_attempted:
                            print("⚠️ WARNING: Message stuck in outbox (Clock) for >60s. Attempting session recovery...")
                            reload_attempted = True
                            safe_reload(page)
                            try:
                                page.wait_for_load_state("networkidle", timeout=15000)
                            except Exception as e:
                                print(f"  [Reload] wait_for_load_state timed out/failed ({e}). Continuing.")
                    else:
                        is_stuck_in_outbox = False
                    
                    time.sleep(4)

            except Exception as e:
                print(f"❌ FAILURE: Verification engine crashed ({e})")

            if not delivery_verified:
                if message_confirmed_in_dom and interaction_success and not is_stuck_in_outbox:
                    print(f"⚠️ SOFT SUCCESS: Checkmark not detected for {name}, but message IS in DOM and composer was emptied. Treating as delivered (BUG-048).")
                    delivery_verified = True
                else:
                    reason = "Message stuck in outbox (Clock icon detected)" if is_stuck_in_outbox else "Checkmark not detected"
                    screenshot_name = f"diag_delivery_failed_{name.replace('/', '_')}_{datetime.now().strftime('%H%M')}.png"
                    print(f"❌ FAILURE: Delivery could not be verified for {name} ({reason}). Saving {screenshot_name}")
                    safe_screenshot(page, screenshot_name)
                    any_failure = True
                    if is_stuck_in_outbox:
                        needs_maintenance = True

            time.sleep(5)

        print("\nAll recipients processed. Finalizing buffer flush (60s)...")
        # EXTENDED: Give the slow VM a full minute to ensure all WebSockets are closed cleanly
        time.sleep(60)
        context.close()
        return not any_failure, needs_maintenance


if __name__ == "__main__":
    import sys
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    # Check for flags
    disco = "--discovery" in sys.argv
    run_broadcaster(message_text="Discovery Test", headless=False, discovery_mode=disco)
