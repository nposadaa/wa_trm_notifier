# Phase 3 Research: Group Messaging Feasibility

The goal was to investigate the best path for broadcasting TRM updates to WhatsApp Groups using the Meta Cloud API.

## Findings

> [!CAUTION]
> **Conclusion**: The official WhatsApp Business Platform (API) does **not** support sending messages to standard WhatsApp groups. This is a fundamental platform restriction, not a business verification issue.

### 1. Group API Restrictions
- Standard WhatsApp groups (the ones users create manually) are entirely inaccessible via the Business API for sending messages.
- Any service claiming to allow this typically uses "unofficial" (scraping-based) methods that carry a high risk of permanent phone number bans.

### 2. Initial Pivot: Individual Broadcasting (Phase 3.1)
Since we cannot post to a group, the next best alternative was to send the same template message to a list of individual recipients via the API. 
**Status**: Skipped. The user explicitly wants group messaging.

### 3. Ultimate Pivot: Playwright Hybrid Automation (Phase 3.2)
We decided to bypass API limitations by automating the WhatsApp Web UI.
- We use the Meta API to send the TRM notification to the admin.
- We use `forwarder.py` (Playwright) to find that message and native-forward it to target groups.
- **Pros**: Achieves actual Group posting.
- **Cons**: Requires keeping a machine/action authenticated on WhatsApp Web via QR code. Viable but fragile to UI DOM changes.

## Recommended Technical Path

1.  **Storage**: Use a `recipients.json` file to map exact names of target Groups and Contacts exactly as they appear in the UI.
2.  **Orchestration Hybrid**: 
    - `main.py` scrapes data and triggers the official API to send it to the admin device.
    - `main.py` immediately executes `forwarder.py` (Playwright) which searches for that message and clicks "Forward" to all entries in `recipients.json`.

## Unresolved Questions
- Will WhatsApp Web DOM updates randomly break the Playwright selectors? (We must ensure selectors are as resilient as possible).
