import os
import glob

# Constants
USER_DATA_DIR = "./whatsapp_session"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"

def clean_browser_locks():
    """Removes orphaned LevelDB and Singleton locks left by unclean kills."""
    try:
        for lock in glob.glob(os.path.join(USER_DATA_DIR, "**", "LOCK"), recursive=True):
            os.remove(lock)
            print(f"[config] Cleaned up stale LevelDB lock: {lock}")
        for singleton in glob.glob(os.path.join(USER_DATA_DIR, "Singleton*")):
            os.remove(singleton)
            print(f"[config] Cleaned up stale Singleton lock: {singleton}")
    except Exception as e:
        print(f"[config] Lock cleanup partial failure: {e}")

def get_browser_context(playwright, headless=True):
    """Returns a hardened, persistent browser context strictly tuned for wa_trm_notifier VMs."""
    args = [
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
        "--unlimited-storage"  # Crucial for low-disk micro VMs
    ]

    print(f"[config] Launching Playwright browser (headless={headless}) with session at {USER_DATA_DIR}...")
    context = playwright.chromium.launch_persistent_context(
        user_data_dir=USER_DATA_DIR,
        headless=headless,
        user_agent=USER_AGENT,
        viewport={'width': 1024, 'height': 768},
        permissions=['notifications', 'background-sync'],
        timezone_id="America/Bogota",
        locale="es-419",
        args=args
    )
    return context

def apply_stealth_overrides(page):
    """Injects JavaScript to normalize the browser fingerprint and prevent bot detection."""
    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {get: () => false});
        Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
        Object.defineProperty(navigator, 'languages', {get: () => ['es-419', 'es', 'en-US', 'en']});
    """)
