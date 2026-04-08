import time
from playwright.sync_api import sync_playwright
from browser_config import clean_browser_locks, get_browser_context

def main():
    print("--- WhatsApp CLI Authenticator ---")
    print("Use this tool locally to generate or refresh a `whatsapp_session` folder.")
    print("Please keep your phone ready.")

    clean_browser_locks()
    
    with sync_playwright() as p:
        context = get_browser_context(p, headless=False)
        page = context.pages[0]
        
        print("Navigating to WhatsApp Web...")
        page.goto("https://web.whatsapp.com/", timeout=120000, wait_until="domcontentloaded")
        
        print("Waiting for QR Code or Chat Sync...")
        session_state = "UNKNOWN"
        elapsed = 0
        
        while elapsed < 600:  # 10 minutes max wait for humans
            if page.get_by_text("Loading your chats").or_(page.get_by_text("Cargando tus chats")).first.is_visible() or page.locator('#pane-side').is_visible():
                session_state = "LOGGED_IN"
                break
                
            if page.locator('canvas, [data-testid="qrcode-container"]').first.is_visible():
                if session_state != "QR_REQUIRED":
                    print("\n⚡ QR CODE IS LIVE!")
                    print("!!! SCAN WITH YOUR PHONE NOW !!!")
                    print("This window will stay open and poll until successfully logged in.")
                    session_state = "QR_REQUIRED"
            
            time.sleep(5)
            elapsed += 5
            
        if session_state == "LOGGED_IN":
            print("\n✅ Session successfully synchronized!")
            print("To ensure keys are safely written to DB, waiting 10 seconds before closing...")
            time.sleep(10)
        else:
            print("\n❌ Timeout (10m) waiting for successful login.")
            
        print("Closing browser cleanly...")
        context.close()
        
        print("\nSession directory is safe to zip and transfer!")
        
if __name__ == "__main__":
    main()
