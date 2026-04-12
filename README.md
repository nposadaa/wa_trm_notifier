# 🚀 WhatsApp TRM Notifier

An automated daily service that scrapes the Colombian Peso (COP) to USD exchange rate (TRM) and broadcasts notifications directly to configured WhatsApp groups and contacts.

## 🌟 Vision
In Colombia, the USD/COP exchange rate is a critical business and social metric. This project provides a reliable, "set-it-and-forget-it" heartbeat service that keeps stakeholders informed every morning.

## 🏗 Architecture
```
dolar-colombia.com → scraper.py → main.py → broadcaster.py → WhatsApp Web (Playwright)
```
1. **Scraper** fetches the official TRM from `dolar-colombia.com`.
2. **Main** formats a clean message string with the date and value.
3. **Broadcaster** opens WhatsApp Web via Playwright, searches for each recipient, types the message, and sends.

## ✨ Key Features
- **Automated Scraper**: Robust Python-based scraper for `dolar-colombia.com`.
- **Direct Browser Broadcast**: Uses **Playwright** to natively type and send messages on WhatsApp Web — no Meta API or business account needed.
- **Multi-Recipient**: Configurable list of groups/contacts via `recipients.json`.
- **Persistent Session**: QR code scan needed only once; session persists across runs.
- **Zero-Cost**: No paid APIs. Runs entirely with free Python tooling.

## 🛠 Tech Stack
- **Language**: Python 3.10+
- **Libraries**: `requests`, `BeautifulSoup4`, `playwright`, `playwright-stealth`
- **Messaging**: WhatsApp Web (Playwright Automation)

## 📁 Project Structure
| File | Purpose |
|------|---------|
| `main.py` | Orchestrator: scrape → format → broadcast |
| `scraper.py` | Fetches TRM data from dolar-colombia.com |
| `broadcaster.py` | Playwright automation for WhatsApp Web |
| `recipients.json` | List of WhatsApp chats to send to |
| `.gsd/` | Project planning & methodology docs |

## 🚀 Getting Started
1. **Clone**:
   ```bash
   git clone https://github.com/nposadaa/wa_trm_notifier.git
   cd wa_trm_notifier
   ```
2. **Setup Environment**:
   ```bash
   py -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   playwright install chromium
   ```
3. **Configure Recipients** — edit `recipients.json`:
   ```json
   {
     "recipients": [
       { "name": "My Group Name", "type": "group" },
       { "name": "Contact Name", "type": "contact" }
     ]
   }
   ```
   > ⚠️ Names must match exactly as they appear in WhatsApp. No emojis.

4. **First Run (QR Scan)** — scan once to establish session:
   ```bash
   py broadcaster.py --discovery
   ```
5. **Run Pipeline**:
   ```bash
   py main.py
   ```

## 🔍 Troubleshooting & Diagnostics
When running on the cloud (GCP VM), use the following utility to sync logs and screenshots to your local machine for analysis:

```powershell
# Sync remote logs and screenshots to local machine
.\scripts\fetch-logs.ps1
```
*(Requires `gcloud` SDK installed and configured on your local machine)*

## 📊 Status
- ✅ Phase 1: Scraper — Complete
- ✅ Phase 2: API Handshake — Complete (deprecated in Phase 3.3)
- ✅ Phase 3: Direct Playwright Broadcast — Complete
- 🚧 Phase 4: Cloud Automation (GCP) — In Progress

---
*Built with the **Get Shit Done (GSD)** methodology.*