# Phase 3 Research: Group Messaging Feasibility

The goal was to investigate the best path for broadcasting TRM updates to WhatsApp Groups using the Meta Cloud API.

## Findings

> [!CAUTION]
> **Conclusion**: The official WhatsApp Business Platform (API) does **not** support sending messages to standard WhatsApp groups. This is a fundamental platform restriction, not a business verification issue.

### 1. Group API Restrictions
- Standard WhatsApp groups (the ones users create manually) are entirely inaccessible via the Business API for sending messages.
- Any service claiming to allow this typically uses "unofficial" (scraping-based) methods that carry a high risk of permanent phone number bans.

### 2. Proposed Pivot: Individual Broadcasting
Since we cannot post to a group, the next best alternative is to send the same template message to a list of individual recipients. 

- **Pros**: 100% official, uses existing `whatsapp_client.py` logic, no risk of bans.
- **Cons**: Recipients receive messages in their private chat rather than a group.
- **Limit**: Unverified accounts can send to ~250 unique conversations every 24 hours (plenty for this project).

## Recommended Technical Path

1.  **Storage**: Move from a single `RECIPIENT_PHONE_NUMBER` in `.env` to a `recipients.json` file to manage multiple contacts easily.
2.  **Orchestration**: Update `main.py` to iterate through the JSON list and call `client.send_template_message` for each.
3.  **Opt-in Management (v1)**: Users must be added manually to the JSON file by the admin.

## Unresolved Questions
- Should we investigate "WhatsApp Channels"? (Likely too public/complex for this use case, but an option for pure broadcasting).
