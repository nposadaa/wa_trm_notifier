# Changelog

All notable changes to the WhatsApp TRM Notifier project will be documented in this file.

## [1.1.1] - 2026-05-04
> **Status**: Released. Critical fixes for WhatsApp Web React DOM updates.

### Fixed
- **React DOM Sync**: Changed the trigger from `press("Space")` to `type(" ", delay=50)` to ensure full IME events are fired, forcing WhatsApp's React state to wake up and reveal the Send button.
- **Send Button Locator**: Broadened the Send button locators to include `data-icon="send"` and `aria-label` fallbacks to combat recent WhatsApp Web DOM changes.
- **Verification Hardening (Hotfix)**: The script now polls the DOM for up to 30 seconds to allow slow 1-core VMs to render the new message row before enforcing the strict snippet match.
- **CRON Documentation**: Reverted the documented schedule in `CRON_SETUP.md` back to `0 12` (7:00 AM COT) to match the deployed state.

## [1.1.0] - 2026-05-03
> **Status**: Released. Financial Intelligence (Phase 1 & 2).

### Added
- **Trend Indicator (📈/📉/➖)**: The broadcaster now compares the current TRM with the previous trading day's rate and calculates the delta in the message.
- **Weekday Optimization**: Modified scheduling instructions to only execute Monday-Friday, skipping the weekends to save GCP compute resources.
- **Dry-Run Mode**: Added a `--dry-run` flag to `main.py` allowing users to preview the exact formatted message without invoking the WhatsApp Web headless browser.

## [1.0.8] - 2026-04-30
> **Status**: Released. Resource-efficiency patch and verification hardening.

### Fixed
- **(BUG-014)** Implemented automatic profile bloat cleanup (`Cache`, `Code Cache`, `GPUCache`, etc.) in `browser_config.py` to prevent OOM/browser freezes on 1GB RAM VMs.
- **(BUG-015)** Hardened delivery verification by stripping emojis from match snippets, preventing false-negative mismatches on slow/headless browsers.
- **(BUG-016)** Added Xvfb lock cleanup (`/tmp/.X99-lock`) to `run_vm.sh` to prevent startup failures after unclean kills.
- **Code Cleanup**: Removed redundant NameError in `broadcaster.py` and duplicate screenshot blocks in failure handlers.

## [1.0.7] - 2026-04-24
> **Status**: Released. Outbox recovery and fail-state detection hardening.

### Fixed
- **(BUG-010)** Implemented `jumpstart reload` in `connectivity_guard` to resolve WebSocket hangs when the "Connecting to WhatsApp" banner persists.
- **(BUG-011)** Added `recovery reload` for outbox hangs (Clock icon); script now reloads the page if a message is stuck for >60s and re-verifies delivery.
- **(BUG-012)** Hardened `connectivity_guard` selectors to catch modern WhatsApp Web alert banners (`[data-testid="connectivity-banner"]`, `[role="alert"]`).
- **(BUG-013)** Added explicit detection for "Failed to send" (Red exclamation) status to avoid unnecessary timeouts.
- **Improved Verification**: Fixed false-positive in message presence check by normalizing emoji/text comparison in the anchored chat row.

## [1.0.6] - 2026-04-19
> **Status**: Released. Stability patch for high-latency VM environments.

### Fixed
- **Verification Buffer**: Added a 2s settle-pause before delivery verification to allow the React DOM to stabilize.
- **Extended Timeout**: Increased delivery verification timeout to 5 minutes (300s) to handle extreme "acknowledgment lag" on 1-core VMs.
- **Granular Logging**: Added elapsed time tracking for the acknowledgment wait to improve observability of VM performance.

## [1.0.5] - 2026-04-19
> **Status**: Released. Delivery verification hardening and connectivity guards.

### Fixed
- **(BUG-008)** Anchor delivery verification to the physical last message row in the chat pane to prevent false-positives from previous messages.
- **(BUG-009)** Hardened connectivity guard with broader selectors (`data-icon`) and implemented a re-verification check immediately before message composition.

## [1.0.4] - 2026-04-17
> **Status**: Released. Data source migration and delivery verification hardening.

### Planned
- **(FEATURE)** Migrate TRM scraper source from `dolar-colombia.com` to the official SuperFinanciera Datos Abiertos API (Socrata) for improved timeliness. Update message template to cite `www.superfinanciera.gov.co`.
### Fixed
- **(BUG-007)** Fix false-negative delivery verification: update checkmark selectors to match current WhatsApp DOM (adding `data-icon`); use `wait_for(state="attached")` and treat absence of clock icon as likely success.

## [1.0.3] - 2026-04-14
> **Status**: Released. Fixes delivered in Phase 5 / Sprint 3 (typing & scraper).
> Bugs are tracked in `.gsd/phases/5/BUGS.md`.

### Fixed
- **(BUG-005)** CRON shifted from 7:00 AM to 10:00 AM COT to ensure `dolar-colombia.com`
  has updated the day's TRM. Added staleness check with disclaimer in `main.py`.
- **(BUG-006)** Replaced `press_sequentially` + `element_handle()` + `execCommand('insertText')`
  with `page.keyboard.insert_text()` — dispatches proper browser-level InputEvent compatible
  with WhatsApp's Lexical editor. Handles emoji/Unicode natively. Post-typing verification added.

### Changed
- CRON schedule: `0 12 * * *` → `0 15 * * *` (10:00 AM COT)

## [1.0.2] - 2026-04-14
> **Status**: Released. Fixes delivered in Phase 5 / Sprint 2 (delivery-reliability).
> Bugs are tracked in `.gsd/phases/5/BUGS.md`.

### Fixed
- **(BUG-001)** Pre-send connectivity guard: broadcaster now detects "Connecting/Retrying" banner
  before attempting to send; aborts cleanly with error if WebSocket is not restored within 60s.
- **(BUG-002)** Exit code propagation: `main.py` now exits with code `1` when the broadcaster
  reports a delivery failure, ensuring CRON and log pipelines reflect true execution status.
- **(BUG-003)** Safe diagnostic screenshots: all `page.screenshot()` calls wrapped in
  `safe_screenshot()` with 10s timeout and try/except to prevent error-handler crashes.
- **(BUG-004)** Typing timeout increase: `press_sequentially` timeout raised from 30s to 60s
  and `wait_for` from 45s to 60s to accommodate e2-micro CPU load during E2E sync.

## [1.0.1] - 2026-04-13
### Added
- **UI Janitor**: Automatic dismissal of "Notifications are off" and "Update" banners during login to optimize DOM stability.
- **Reinforced Interaction**: Implemented 2-attempt typing retry loop and increased timeouts (45s) for message input box to survive high VM load.
- **JS-Force Focus**: Added `document.execCommand` injection to force focus on message input box, bypassing Playwright's bounding-box jitter checks.

## [1.0.0] - 2026-04-12

### Added
- **Self-Healing Locators (DEC-021)**: Switched to dynamic queries that automatically recover if the DOM re-renders during high CPU load.
- **Sync Watchdog & Progress Detection**: Real-time percentage detection and automated `page.reload()` to jumpstart hanging decryption syncs.
- **Remote Diagnostics Utility**: Created `scripts/fetch-logs.ps1` for seamless local analysis of cloud failures.
- **Patience Patch**: Extended delivery verification to 3 minutes to handle slow WebSocket uploads on 1-core VMs.

### Changed
- Standardized project runner to `scripts/run_vm.sh`.
- Optimized V8 memory flags (`--max-old-space-size=640`) for e2-micro instances.

## [1.0.0-beta] - 2026-04-08

### Added
- Scraper pipeline for `dolar-colombia.com` to grab live TRM data.
- Automated formatting of TRM data into a stylized WhatsApp message.
- Full Playwright integration to bypass WhatsApp Business API restrictions.
- Persistent session storage (`whatsapp_session/`) to skip repeated QR scanning.
- Auto-cleanup of `SingletonLock` on VM boot to handle headless VM crash loops.
- Advanced diagnostic logging spanning both Python stdout and inner-browser console dumps.

### Changed
- Pivoted from Meta Cloud API to a GUI-based Playwright architecture.
- Replaced mouse-based queries with pure keyboard-driven navigation (`Shift+Enter` for line breaks) to improve resilience on headless VMs.
- Upgraded strict Playwright locators to native structural anchors (`#main div[contenteditable="true"]`) to overcome React Lexical re-render timeouts.

### Fixed
- Fixed Playwright `TimeoutError` in the chat composer by freezing `element_handle`.
- Re-enabled GPU flags to prevent immediate compositor hard-stalls on GCP e2-micro VMs.
- Patched delivery verification to wait for physical checkmarks (`msg-check`) instead of blindly trusting keystrokes.
