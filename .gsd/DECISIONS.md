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
- **Status**: Deprecated (replaced by DEC-005)

## DEC-003: Playwright Pivot for Group Messaging
- **Date**: 2026-04-06
- **Phase**: 3.1
- **Decision**: Use Playwright browser automation instead of Meta API for group messaging.
- **Rationale**: Meta Cloud API does not support standard WhatsApp groups without extreme business verification.
- **Status**: Active (evolved into DEC-005)

## DEC-004: Persistent WhatsApp Session
- **Date**: 2026-04-06
- **Phase**: 3.2
- **Decision**: Store Playwright browser session in ./whatsapp_session/ to avoid repeated QR scans.
- **Rationale**: QR scan only needed once; session reused across runs.
- **Status**: Active

## DEC-005: Direct Broadcast - Remove Meta API Entirely
- **Date**: 2026-04-06
- **Phase**: 3.3
- **Decision**: Bypass Meta API completely. Scraper feeds formatted text directly to Playwright, which types and sends natively in each chat.
- **Rationale**: Forwarding via context menus proved extremely fragile due to WhatsApp Web DOM changes. Direct typing is simpler, more robust, and eliminates the API dependency entirely.
- **Alternatives Rejected**: Meta API + Playwright forwarding (too brittle), Meta API only (cant reach groups).
- **Status**: Active

## DEC-006: No Emojis in recipients.json
- **Date**: 2026-04-06
- **Phase**: 3.3
- **Decision**: Use plain text names only in recipients.json.
- **Rationale**: Emojis cause encoding issues in Playwright search - chat not found.
- **Status**: Active

## DEC-008: Hybrid Search Trigger (fill + Enter)
- **Date**: 2026-04-08
- **Phase**: 4.1
- **Decision**: Use `fill()` to input search text, followed by an explicit `press("Enter")`.
- **Rationale**: `fill()` is memory-efficient for the 1GB VM but doesn't always trigger the search UI. `Enter` forces the React state to update without the high CPU overhead of character-by-character `type()`.
- **Status**: Active

## DEC-009: Advanced Diagnostics (Console + Sidebar Audit)
- **Date**: 2026-04-08
- **Phase**: 4.1
- **Decision**: Implement real-time mirroring of browser console errors to VM stdout and automated sidebar text audits on failure.
- **Rationale**: Debugging headless runs on remote VMs is difficult. Console logs and DOM dumps at the moment of failure provide immediate root-cause evidence.
- **Status**: Active

## DEC-010: Delivery Safety Buffer
- **Date**: 2026-04-08
- **Phase**: 4.1
- **Decision**: Add a 10-second sleep after all messages are processed before closing the context.
- **Rationale**: Slow VMs often kill the browser process before the last message has finished uploading via WebSockets, even if the UI reports success.
- **Status**: Active

