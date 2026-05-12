import os
import glob
import shutil

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
    
    # Also clean cache bloat (DEC-035)
    clean_browser_bloat()
    
    # Check for maintenance flag (BUG-018)
    if os.path.exists(".gsd/needs_maintenance"):
        print("[config] 🛠 Maintenance flag detected. Performing DEEP CLEAN...")
        deep_clean_profile()

def clean_browser_bloat():
    """Removes Cache and Code Cache directories to prevent profile bloat on e2-micro."""
    bloat_paths = [
        os.path.join(USER_DATA_DIR, "Default", "Cache"),
        os.path.join(USER_DATA_DIR, "Default", "Code Cache"),
        os.path.join(USER_DATA_DIR, "Default", "GPUCache"),
        os.path.join(USER_DATA_DIR, "Default", "Service Worker", "CacheStorage"),
        os.path.join(USER_DATA_DIR, "Default", "Service Worker", "ScriptCache"),
        os.path.join(USER_DATA_DIR, "Default", "Blob Storage"),
        os.path.join(USER_DATA_DIR, "GrShaderCache"),
        os.path.join(USER_DATA_DIR, "ShaderCache"),
    ]
    for path in bloat_paths:
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
                print(f"[config] Cleaned up bloat directory: {path}")
            except Exception as e:
                print(f"[config] Bloat cleanup warning for {path}: {e}")

def deep_clean_profile():
    """Removes IndexedDB and Service Worker to force a fresh sync (preserves LocalStorage session)."""
    deep_paths = [
        os.path.join(USER_DATA_DIR, "Default", "IndexedDB"),
        os.path.join(USER_DATA_DIR, "Default", "Service Worker"),
    ]
    for path in deep_paths:
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
                print(f"[config] DEEP CLEAN: Removed {path}")
            except Exception as e:
                print(f"[config] DEEP CLEAN warning for {path}: {e}")

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
        "--js-flags='--max-old-space-size=640'", 
        "--disable-setuid-sandbox",
        "--no-first-run",
        "--disable-background-networking",
        "--disable-web-security",
        "--password-store=basic",
        "--use-mock-keychain",
        "--disable-features=IsolateOrigins,site-per-process,Translate,OptimizationHints,MediaRouter,DialMediaRouteProvider,ProcessPerSiteUpToMainFrameThreshold",
        "--disable-component-update",
        "--disable-extensions",
        "--unlimited-storage"
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
        
        // Mock persistent storage to prevent WhatsApp crash in headless Linux
        if (navigator.storage) {
            navigator.storage.persist = async () => true;
            if (!navigator.storage.estimate) {
                navigator.storage.estimate = async () => ({ quota: 1000000000, usage: 10000000 });
            }
        }
    """)
