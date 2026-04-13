# Changelog

All notable changes to the WhatsApp TRM Notifier project will be documented in this file.

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
