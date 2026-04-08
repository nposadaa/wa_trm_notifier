import time
from playwright.sync_api import sync_playwright

def inspect_chat_box():
    with sync_playwright() as p:
        USER_DATA_DIR = "./whatsapp_session"
        USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        
        context = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=True,
            user_agent=USER_AGENT,
            viewport={'width': 1024, 'height': 768},
            args=["--disable-gpu", "--no-sandbox"]
        )
        
        page = context.new_page()
        page.goto("https://web.whatsapp.com/")
        print("Waiting for chat pane...")
        
        if page.locator('#pane-side, [data-testid="chat-list-search-filtered"]').first.is_visible(timeout=60000):
            print("Logged in!")
        else:
            print("Not logged in or too slow")
            context.close()
            return
            
        time.sleep(5)
        # Search for COP/USD Notifier
        search_box = page.locator('#side [contenteditable="true"]').first
        search_box.focus()
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        page.keyboard.type("COP/USD Notifier", delay=50)
        time.sleep(2)
        page.keyboard.press("Enter")
        
        time.sleep(3)
        print("Grabbing footer HTML...")
        footer = page.locator('footer')
        if footer.is_visible():
            print(footer.evaluate("el => el.outerHTML"))
            print("---")
            textbox = page.locator('#main').get_by_role("textbox", name="Type a message").or_(page.locator('#main').get_by_role("textbox", name="Escribe un mensaje")).first
            print("textbox via role found:", textbox.count() if hasattr(textbox, 'count') else "yes")
            if textbox.is_visible():
                print("textbox html:", textbox.evaluate("el => el.outerHTML"))
        else:
            print("No footer found in #main")
            
        context.close()

if __name__ == "__main__":
    inspect_chat_box()
