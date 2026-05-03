# WhatsApp Message Templates

These are the templates for the **TRM Notifier**. You must register these in the Meta Developer Portal exactly as shown to match the Python script's logic.

---

## 1. trm_daily_official (Phase 2)
Used for the core daily TRM broadcast to your test phone number.

**Name**: `trm_daily_official`  
**Category**: Utility  
**Language**: English (US) / `en_US`  

### Body Text
> `Good morning! Today, {{1}}, the official USD/COP exchange rate (TRM) is set at ${{2}}. Have a great day!`

### Variables (Params)
- `{{1}}`: The Date (e.g., `2026-04-02`)
- `{{2}}`: The TRM Value (e.g., `3675.81`)

---

## Instructions for Registration
1. Go to **WhatsApp > Message Templates** in the Meta Developer Dashboard.
2. Click **Create Template**.
3. Select **Category: Utility** and **Language: English (US)**.
4. Copy the **Body Text** above.
5. In the "Variables" section, ensure you add two samples (one for the date, one for the price) so Meta can approve it.
6. Click **Submit**.

---

*Last updated: 2026-04-02*
