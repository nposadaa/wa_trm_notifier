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

## DEC-019: Structure-First Lexical Input Strategy (Anti-Timeout)
- **Date**: 2026-04-08
- **Phase**: 4.5
- **Decision**: Replace `get_by_role("textbox", name="...")` with `#main div[contenteditable="true"]`, freeze it using `.element_handle()`, and send strings line-by-line using `page.keyboard.type` with `Shift+Enter` for newlines.
- **Rationale**: 
  1. *Locator Timeouts*: WhatsApp's React-based Lexical editor dynamically changes `aria-label` properties the millisecond text is entered. Playwright's `press_sequentially` constantly re-evaluates the locator between keystrokes and crashes with a 30s `TimeoutError` when the label vanishes. `element_handle` freezes the DOM reference, bypassing actionability timeouts.
  2. *Premature Sending*: Standard Playwright string typing interprets `\n` as `Enter`, triggering WhatsApp's native "Send" event halfway through multi-line messages (like the TRM breakdown). Manually shifting down for `Enter` preserves the line breaks without triggering submission.
- **Relation**: Replaces **DEC-018**'s `press_sequentially` standard and corrects localized query failure points.
- **Status**: Active
