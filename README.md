# 🚀 WhatsApp TRM Notifier

An automated daily service that scrapes the Colombian Peso (COP) to USD exchange rate (TRM) and broadcasts notifications directly to configured WhatsApp groups and contacts.

## 🌟 Vision
In Colombia, the USD/COP exchange rate is a critical business and social metric. This project provides a reliable, "set-it-and-forget-it" heartbeat service that keeps stakeholders informed every morning.

## 🏗 Architecture
```
datos.gov.co (Datos Abiertos) → scraper.py → main.py → broadcaster.py → WhatsApp Web (Playwright)
```
1. **Scraper** fetches the official TRM directly from the `datos.gov.co` (SuperFinanciera Socrata API).
2. **Main** formats a clean message string with the date and value.
3. **Broadcaster** opens WhatsApp Web via Playwright, searches for each recipient, types the message, and sends.

## ✨ Key Features
- **Automated Scraper**: Extremely fast API consumer built exclusively for the official Colombian `Datos Abiertos` infrastructure.
- **Financial Intelligence**: Dynamic message formatting computes rate changes between trading days with emojis (📈/📉/➖) and exact delta values.
- **Direct Browser Broadcast**: Uses **Playwright** to natively type and send messages on WhatsApp Web — no Meta API or business account needed.
- **Weekday Scheduling**: Optimized to run Monday-Friday, preserving compute resources on non-trading days.
- **Self-Healing Interaction**: Uses Playwright **Locators** (DEC-021) to automatically recover if the DOM re-renders during slow cloud syncs.
- **Zero-Cost**: Runs entirely on a GCP "Always Free" e2-micro instance.
- **Diagnostic-First**: Includes robust remote logging and failure-screenshot sync tools.

## 📁 Project Documentation
For detailed guides on specific modules, refer to:
| Document | Purpose |
| :--- | :--- |
| [GCP_SETUP.md](docs/GCP_SETUP.md) | How to provision a $0.00/mo server in the Google Free Tier. |
| [CRON_SETUP.md](docs/CRON_SETUP.md) | How to schedule the daily run on a Linux server. |
| [SESSION_TRANSFER.md](docs/SESSION_TRANSFER.md) | The "Zip & Ship" authentication workflow. |
| [Runbook](docs/runbook.md) | Operational procedures and troubleshooting patterns. |
| [Decisions](.gsd/DECISIONS.md) | Architectural History (The "Why"). |

---

## 🚀 Getting Started (Local Development)

1. **Clone & Setup**:
   ```bash
   git clone https://github.com/nposadaa/wa_trm_notifier.git
   cd wa_trm_notifier
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **First Run (QR Scan)**:
   ```bash
   python broadcaster.py --discovery
   ```

3. **Local Run**:
   ```bash
   python main.py
   ```

---

## ☁️ Cloud Deployment (GCP stabilization)

Because GCP e2-micro instances have limited RAM (1GB), we use a **"Zip & Ship"** authentication strategy to prevent decryption-related crashes.

### 1. Provisioning
Follow the [GCP_SETUP.md](docs/GCP_SETUP.md) guide to create your free e2-micro instance.

### 2. The "Zip & Ship" Authentication
Establish your session locally where you have more RAM, then transfer the results to the cloud. See the [SESSION_TRANSFER.md](docs/SESSION_TRANSFER.md) for step-by-step details:
1. Run `python auth.py` locally and scan the QR code.
2. Wait for the phone to show "Active" and press `Enter` to save.
3. Zip the session: `Compress-Archive -Path whatsapp_session -DestinationPath whatsapp_session.zip`.
4. Upload to VM: `gcloud compute scp whatsapp_session.zip [USER]@[VM]:~/wa_trm_notifier/`.

### 2. Cloud Execution
On your Linux instance, use the standardized runner to handle the virtual display and logging:
```bash
bash scripts/run_vm.sh
```

### 3. Monitoring & Diagnostics
If the cloud run fails or times out, pull the remote evidence to your local machine for analysis:
```powershell
# Run from local PowerShell
.\scripts\fetch-logs.ps1
```

---

## 📊 Status
- ✅ Phase 1: Scraper — Complete
- ✅ Phase 2: API Handshake — Complete (deprecated in Phase 3.3)
- ✅ Phase 3: Direct Playwright Broadcast — Complete
- ✅ Phase 4: Cloud Automation (GCP) — Deployed & Running
- 🔄 Phase 5: Live Support & Stability — Active

### Phase 5 — Live Support Model
Post-deployment reliability work is managed in **time-boxed sprints** rather than monolithic planning cycles. Each sprint targets specific bugs or improvements surfaced from autonomous CRON runs.

| Artifact | Purpose |
| :--- | :--- |
| [BUGS.md](.gsd/phases/5/BUGS.md) | Active bug tracker — every bug linked to a release tag |
| [SPRINT.md](.gsd/SPRINT.md) | Current sprint scope and task status |
| [CHANGELOG.md](CHANGELOG.md) | Release history — every fix referenced by `BUG-NNN` ID |

> **Current version**: `v1.1.3` — Critical Fix for Wrong Chat Selection (Text Fallback bug)

---
*Built with the **Get Shit Done (GSD)** methodology.*
