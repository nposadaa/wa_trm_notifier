import time
import os
import argparse
from playwright.sync_api import sync_playwright
from browser_config import clean_browser_locks, get_browser_context, apply_stealth_overrides

def main():
    parser = argparse.ArgumentParser(description="WhatsApp CLI Authenticator")
    parser.add_argument("--headless", action="store_true", help="Run headlessly on the cloud to generate qr.png")
    args = parser.parse_args()

    print("--- WhatsApp CLI Authenticator ---")
    if args.headless:
        print("Running in HEADLESS mode. A 'qr.png' will be generated for you to download and scan.")
    else:
        print("Running in UI mode. Please keep your phone ready.")

    clean_browser_locks()
    
    with sync_playwright() as p:
        context = get_browser_context(p, headless=args.headless)
        page = context.pages[0]
        apply_stealth_overrides(page)
        
        print("Navigating to WhatsApp Web...")
        page.goto("https://web.whatsapp.com/", timeout=120000, wait_until="domcontentloaded")
        
        print("Waiting for QR Code or Chat Sync...")
        session_state = "UNKNOWN"
        elapsed = 0
        
        while elapsed < 2400:  # 40 minutes max wait for humans
            if page.locator('#pane-side, [data-testid="chat-list-search-filtered"]').first.is_visible():
                session_state = "LOGGED_IN"
                break
                
            if page.get_by_text("Loading your chats").or_(page.get_by_text("Cargando tus chats")).first.is_visible():
                print(f"\n[{elapsed}s] Syncing detected... waiting up to 30 minutes for E2E keys to download on slow hardware.")
                try:
                    page.wait_for_selector('#pane-side, [data-testid="chat-list-search-filtered"]', timeout=1800000)
                    session_state = "LOGGED_IN"
                    break
                except Exception:
                    pass
                
            if page.locator('canvas, [data-testid="qrcode-container"]').first.is_visible():
                if session_state != "QR_REQUIRED":
                    print("\n⚡ QR CODE IS LIVE!")
                    if args.headless:
                        print("!!! qr.png IS BEING UPDATED. PLEASE DOWNLOAD IT NOW TO SCAN !!!")
                    else:
                        print("!!! SCAN WITH YOUR PHONE NOW !!!")
                    print("This script will poll for up to 10 minutes until successfully logged in.")
                    session_state = "QR_REQUIRED"
                
                if args.headless:
                    try:
                        # Continuously update the screenshot because WhatsApp rotates the QR every 20s
                        page.screenshot(path="qr.png")
                    except Exception as e:
                        pass
            
            time.sleep(5)
            elapsed += 5
            
        if session_state == "LOGGED_IN":
            print("\n✅ Session successfully synchronized!")
            
            if os.path.exists("qr.png"):
                try:
                    os.remove("qr.png")
                    print("Local qr.png deleted.")
                except Exception as e:
                    pass
            
            if args.headless:
                print("Headless mode: Waiting 180 seconds to ensure E2E keys and chat history are fully downloaded and written to IndexedDB...")
                for i in range(180, 0, -10):
                    print(f"Waiting... {i} seconds remaining.")
                    time.sleep(10)
            else:
                print("\n⚠️ IMPORTANT: Do not close immediately!")
                print("WhatsApp Web needs time to download E2E encryption keys and chat history.")
                print("Check your phone's 'Linked Devices' - wait until the status changes from 'Syncing' to 'Active'.")
                input("Press ENTER here to safely close the browser once you confirm it is fully synced...")
                print("Writing final data to disk...")
                time.sleep(5)
                
        else:
            print("\n❌ Timeout (40m) waiting for successful login.")
            
        print("Closing browser cleanly...")
        context.close()
        
        print("\nSession directory is safe to zip and transfer!")
        
if __name__ == "__main__":
    main()
