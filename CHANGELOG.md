# Changelog

All notable changes to the WhatsApp TRM Notifier project will be documented in this file.

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
