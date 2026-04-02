# 🚀 WhatsApp TRM Notifier

An automated daily service that tracking the Colombian Peso (COP) to USD exchange rate (TRM) and broadcasts notifications directly to configured WhatsApp groups.

## 🌟 Vision
In Colombia, the USD/COP exchange rate is a critical business and social metric. This project provides a reliable, "set-it-and-forget-it" heartbeat service that keeps stakeholders informed every morning at 7:00 AM.

## ✨ Key Features
- **Automated Scraper**: Robust Python-based scraper for `dolar-colombia.com`.
- **Official API**: Uses the **Meta WhatsApp Business Cloud API** for secure and reliable delivery.
- **Cloud Native**: Powered by **GitHub Actions** for 100% automated daily runs.
- **Zero-Cost Implementation**: Designed to run entirely within the free tiers of GitHub and Meta.

## 🛠 Tech Stack
- **Language**: Python 3.10+
- **Libraries**: `requests`, `BeautifulSoup4`, `lxml`
- **Infrastructure**: GitHub Actions (Cron Scheduler)
- **Messaging**: Meta WhatsApp Cloud API (Groups API)

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
   ```
3. **Run Locally**:
   ```bash
   py scraper.py
   ```

---
*Developed with the **Get Shit Done (GSD)** methodology.*