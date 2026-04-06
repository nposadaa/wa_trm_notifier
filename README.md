# 🚀 WhatsApp TRM Notifier

An automated daily service that tracking the Colombian Peso (COP) to USD exchange rate (TRM) and broadcasts notifications directly to configured WhatsApp groups.

## 🌟 Vision
In Colombia, the USD/COP exchange rate is a critical business and social metric. This project provides a reliable, "set-it-and-forget-it" heartbeat service that keeps stakeholders informed every morning at 7:00 AM.

## ✨ Key Features
- **Automated Scraper**: Robust Python-based scraper for `dolar-colombia.com`.
- **Browser Automation**: Uses **Playwright** to drive WhatsApp Web, enabling direct forwarding to standard groups and contacts.
- **Cloud Native**: Designed for server deployment (GitHub Actions transition incoming).
- **Zero-Cost Implementation**: Runs entirely within the free tiers of Python tooling.

## 🛠 Tech Stack
- **Language**: Python 3.10+
- **Libraries**: `requests`, `BeautifulSoup4`, `playwright`, `playwright-stealth`
- **Messaging**: WhatsApp Web (Playwright Automation)

## 📁 Project Structure
- `scraper.py`: Core logic for retrieving TRM data.
- `.github/workflows/`: Automation scripts for daily notification triggers.
- `.gsd/`: Internal project specification and methodology (Get Shit Done).

## 🚀 Getting Started (Quick Start)
1. **Clone the repository**:
   ```bash
   git clone https://github.com/nposadaa/wa_trm_notifier.git
   ```
2. **Setup Environment**:
   ```bash
   py -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   playwright install chromium
   ```
3. **Configure Recipients**: Edit `recipients.json` to map WhatsApp Chat names.
4. **First Run (QR Scan)**:
   ```bash
   py forwarder.py --discovery
   ```
5. **Run Entire Pipeline**:
   ```bash
   py main.py
   ```

---
*Developed with the **Get Shit Done (GSD)** methodology.*