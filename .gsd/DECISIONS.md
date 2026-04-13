# DECISIONS.md - Architecture Decisions Register

> Keep track of all technical decisions here.

## DEC-001: Scraper Source
- **Date**: 2026-04-02
- **Phase**: 1
- **Decision**: Use dolar-colombia.com as TRM data source.
- **Rationale**: Reliable, simple HTML structure, no auth required.
- **Status**: Active

## DEC-002: Meta WhatsApp Cloud API for 1-on-1 Messaging
- **Date**: 2026-04-02
- **Phase**: 2
- **Decision**: Use Meta Business Cloud API with template messages for initial delivery.
- **Rationale**: Official API, reliable for 1-on-1 messaging.
- **Status**: Deprecated (replaced by **DEC-005**)

## DEC-003: Playwright Pivot for Group Messaging
- **Date**: 2026-04-06
- **Phase**: 3.1
- **Decision**: Use Playwright browser automation instead of Meta API for group messaging.
- **Rationale**: Meta Cloud API does not support standard WhatsApp groups without extreme business verification.
- **Status**: Active (evolved into **DEC-005**)

## DEC-004: Persistent WhatsApp Session
- **Date**: 2026-04-06
- **Phase**: 3.2
- **Decision**: Store Playwright browser session in `./whatsapp_session/` to avoid repeated QR scans.
- **Rationale**: QR scan only needed once; session reused across runs.
- **Status**: Active

## DEC-005: Direct Broadcast - Remove Meta API Entirely
- **Date**: 2026-04-06
- **Phase**: 3.3
- **Decision**: Bypass Meta API completely. Scraper feeds formatted text directly to Playwright, which types and sends natively in each chat.
- **Rationale**: Forwarding via context menus proved extremely fragile due to WhatsApp Web DOM changes. Direct typing is simpler and more robust.
- **Status**: Active

## DEC-006: No Emojis in recipients.json
- **Date**: 2026-04-06
- **Phase**: 3.3
- **Decision**: Use plain text names only in recipients.json.
- **Rationale**: Emojis caused encoding issues in Playwright search—chat not found.
- **Status**: Active

## DEC-007: Headless Mode Disabled
- **Date**: 2026-04-06
- **Phase**: 3.2
- **Decision**: Run Playwright with `headless=False`.
- **Rationale**: WhatsApp Web detects and blocks headless sessions. 
- **Impact**: Requires a virtual display (XVFB) for server execution.
- **Status**: Active

## DEC-008: Hybrid Search Strategy (fill + Enter)
- **Date**: 2026-04-08
- **Phase**: 4.1
- **Decision**: Use `fill()` to input search text, followed by an explicit `press("Enter")`.
- **Rationale**: `fill()` is memory-efficient for the 1GB VM but doesn't always trigger the search UI. `Enter` forces the React state to update.
- **Implementation**: Refined by **DEC-015** (Structural Locators).
- **Status**: Partially superseded — search box still uses `keyboard.type()` (DEC-016), but **message composition `fill()` is fully replaced by `keyboard.type()` (DEC-018)**.

## DEC-009: Advanced Diagnostics (Console + Sidebar Audit)
- **Date**: 2026-04-08
- **Phase**: 4.1
- **Decision**: Mirror browser console errors to VM stdout and log sidebar text audits on failure.
- **Rationale**: Debugging remote headless runs without visual access requires deep "inner-browser" reporting.
- **Status**: Active

## DEC-010: Delivery Safety Buffer
- **Date**: 2026-04-08
- **Phase**: 4.1
- **Decision**: Add a 10-second sleep after broadcast before closing context.
- **Rationale**: Slow VMs often kill the browser process before the last message uploads via WebSockets.
- **Status**: Active

## DEC-011: Rendering & 3D Disabling (Re-Activated)
- **Date**: 2026-04-08
- **Phase**: 4.3
- **Decision**: Disable 3D APIs, WebGL, and hardware acceleration via flags.
- **Rationale**: Re-activated after proving that removing these flags caused immediate GPU stalls on the e2-micro VM, even in headless mode. 
- **Status**: Active

## DEC-012: Pre-flight SingletonLock Cleanup
- **Date**: 2026-04-08
- **Phase**: 4.2
- **Decision**: Programmatically remove `SingletonLock` from the session folder before launch.
- **Rationale**: Prevents "storage bucket persistence denied" errors after abnormal browser exits on the VM.
- **Status**: Active

## DEC-013: Aggressive Resource Caching Limits
- **Date**: 2026-04-08
- **Phase**: 4.2
- **Decision**: Set disk/media cache sizes to 1 byte.
- **Status**: Deprecated (replaced by **DEC-014**)
- **Rationale**: Likely caused networking handles to exhaust while trying to bypass cache for critical app blobs.

## DEC-014: Safe Stability Pivot (Standard Configuration)
- **Date**: 2026-04-08
- **Phase**: 4.3
- **Decision**: Remove all resource-blocking interceptors and revert to a standard Chromium flag set. 
- **Rationale**: Proved the most stable path for the e2-micro VM; fixed infinite `net::ERR_FAILED` loops.
- **Status**: Active

## DEC-015: Persistent Search Locators (Structural CSS)
- **Date**: 2026-04-08
- **Phase**: 4.3
- **Decision**: Use `#side div[contenteditable="true"]` instead of `get_by_placeholder`.
- **Rationale**: Placeholders disappear after typing, making lazy locators invalid during the `Enter` press step. Structural CSS remains stable.
- **Relation**: Fixes the implementation of **DEC-008**.
- **Status**: Active

## DEC-016: Keyboard-First Interaction (No-Mouse Search)
- **Date**: 2026-04-08
- **Phase**: 4.4
- **Decision**: Use `focus()` and `page.keyboard.type()` instead of `click()` and `fill()` for the search box.
- **Rationale**: Mouse-click actions (`click()`) were timing out despite the element being "stable," indicating a desync between Playwright and the VM's graphics compositor. Keyboard events are processed by the browser's core logic and are more reliable on overloaded hardware.
- **Status**: Active

## DEC-017: Empirical Delivery Verification (Checkmark Audit)
- **Date**: 2026-04-08
- **Phase**: 4.4
- **Decision**: Only report success if a "Sent" (`msg-check`) or "Delivered" (`msg-dblcheck`) icon is detected in the UI after sending.
- **Rationale**: Low-resource VMs often report "Success" after a keystroke even if the UI hasn't committed the message yet. Waiting for the checkmark ensures the message has actually reached the WhatsApp server before closing the browser.
- **Status**: Active

## DEC-018: keyboard.type() for Message Composition (React Event Fix)
- **Date**: 2026-04-08
- **Phase**: 4.5
- **Decision**: Replace `chat_box.fill(message_text)` with `page.keyboard.type(message_text, delay=30)` for composing and sending messages.
- **Rationale**: WhatsApp Web's message input is a `contenteditable` div driven by React. Playwright's `.fill()` injects text directly into the DOM, bypassing React's synthetic event system — WhatsApp's internal state never registers the text, so the Send button stays hidden and Enter sends nothing. `page.keyboard.type()` fires real keystroke events that React listens to, activating the Send button correctly.
- **Relation**: Extends **DEC-016** (Keyboard-First Interaction) from search to message composition. Supersedes `fill()` usage from **DEC-008** for the message send step.
- **Evidence**: First live VM run (2026-04-08) — chat found, message typed, but Send button not visible and checkmark never detected. Root cause confirmed as React event bypass.
- **Status**: Active

## DEC-019: Structure-First Lexical Input Strategy (Anti-Timeout & Anti-Focus Loss)
- **Date**: 2026-04-08
- **Phase**: 4.5
- **Decision**: Replace `get_by_role("textbox")` with an atomic `page.wait_for_selector('#main div[contenteditable="true"]')` to prevent unmount race conditions. Then, inject text using the explicit `box_handle.type()` instead of `page.keyboard.type()`, keeping `Shift+Enter` for newlines.
- **Rationale**: 
  1. *Locator Timeouts & Race Conditions*: WhatsApp's React-based Lexical editor dynamically changes properties during state transitions. Playwright's `press_sequentially` crashes when the label vanishes mid-type. Furthermore, using a two-step `locator.wait_for()` followed by `element_handle()` triggers race conditions on VMs if React unmounts the wrapper between steps. `page.wait_for_selector` locks onto the C++ pointer atomically.
  2. *Focus Stealing*: Global `page.keyboard.type()` dispatches keys into the ether, which can miss the input box if a React render briefly steals focus on a slow VM. Using `box_handle.type()` explicitly targets the exact DOM node.
  3. *Premature Sending*: Standard string typing interprets `\n` as `Enter`, triggering WhatsApp's "Send" event prematurely. Manually shifting down for `Enter` preserves the line breaks.
- **Relation**: Replaces **DEC-018**'s `press_sequentially` standard and corrects localized query failure points.
- **Status**: Active
## DEC-020: Architecture Split (Authentication vs Production Execution)
- **Date**: 2026-04-08
- **Phase**: 4.5
- **Decision**: Decouple the interactive `QR_REQUIRED` polling flow from `broadcaster.py` into a new, dedicated `auth.py` script. Remove `sys.exit` crutches from production workflows and replace them with hard state invalidation exceptions. Share browser invariants via `browser_config.py`.
- **Rationale**: 
  1. *Resource Guarding*: Production runs on cloud cron jobs should absolutely not idle for minutes waiting for QR scans that will never come.
  2. *UX Stability*: Running locally requires the opposite—waiving all wait limits so the user can easily pull out their phone and scan without the script mysteriously killing the connection mid-sync.
- **Relation**: Stabilizes session token generation (Fixes the 400 Bad Request / aquire-persistent-storage-denied crashes related to session invalidation via `pkill`).
- **Status**: Active

## DEC-021: Self-Healing Locator Architecture (Supersedes Handle portion of DEC-019)
- **Date**: 2026-04-12
- **Phase**: 4.6
- **Decision**: Replace all `ElementHandle` (static pointers) for chat interaction with Playwright `Locators` (search-based queries).
- **Rationale**: 
  1. *Stale Element Errors*: `DEC-019` hypothesized that locking onto a DOM pointer was safer. However, on e2-micro VMs, background chat synchronization causes React to frequently unmount and replace the input box. Static handles become "stale" and crash mid-interaction.
  2. *Resiliency*: `Locators` are lazy and auto-retry. If React replaces the input box during a sequence, Playwright automatically re-queries and recovers the new element seamlessly.
- **Status**: Active (Supersedes interaction logic from **DEC-019**)
164: 
165: ## DEC-022: Aggressive Banner & Modal Clearance
166: - **Date**: 2026-04-13
167: - **Phase**: 4.7
168: - **Decision**: Implement a proactive "UI Janitor" step via `page.evaluate` that dismisses common overlays (Updates, "Notifications Off", etc.) before interaction.
169: - **Rationale**: On resource-constrained VMs, the presence of informational banners like "Notifications are off" can cause layout shifts or consume CPU during React re-renders, potentially interfering with Playwright's visibility/stability checks. Removing them immediately upon login cleans the DOM for faster interaction.
170: - **Status**: Active
171: 
172: ## DEC-023: Reinforced Interaction Strategy (Force-Focus + Retry)
173: - **Date**: 2026-04-13
174: - **Phase**: 4.7
175: - **Decision**: 
176:   1. Increase `wait_for` timeouts from 15s to 45s for the message input box.
177:   2. Pre-emptively use `document.execCommand` via `page.evaluate` to focus and clear the input box before typing.
178:   3. Implement a 2-attempt retry loop for the entire typing/sending sequence for each recipient.
179: - **Rationale**: 
180:   1. *VM Lag*: 15s was proven insufficient during peak VM load (DEC-022 failure diagnostic).
181:   2. *Focus Jitter*: Playwright's native `focus()` sometimes fails if the element's bounding box is oscillating mid-render. JS-based focus is more reliable in these scenarios.
182:   3. *Empty Buffers*: Previous failures resulted in "Emergency Enter" on empty boxes. A retry loop ensures we only attempt a send after confirming the text has been successfully injected.
183: - **Status**: Active
