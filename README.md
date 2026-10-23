# 🚀 WhatsApp TRM Notifier

> **Current Version**: `v1.3.1` (2026-10-23)

An automated daily service that scrapes the Colombian Peso (COP) to USD exchange rate (TRM) and the SET-FX spot market close, then broadcasts notifications directly to configured WhatsApp groups and contacts — **twice a day**.

## 🌟 Vision
In Colombia, the USD/COP exchange rate is a critical business and social metric. This project provides a reliable, "set-it-and-forget-it" heartbeat service that keeps stakeholders informed every morning **and** at market close.

## 🏗 Architecture
```
datos.gov.co (SuperFinanciera)   →  scraper.scrape_trm()         ─┐
proxy.icap.com.co (SET-ICAP)     →  scraper.scrape_spot_market()  ┤→ main.py → broadcaster.py → WhatsApp Web (Playwright)
```
1. **Morning Scraper** (`--edition morning`) fetches the official TRM from the `datos.gov.co` Socrata API.
2. **Closing Scraper** (`--edition closing`) fetches the intraday USD/COP spot close from the SET-ICAP official delayed snapshot API.
3. **Main** formats the edition-specific message with values, emojis, and delta.
4. **Broadcaster** opens WhatsApp Web via Playwright, searches for each recipient, types the message, and sends.

## ✨ Key Features
- **Dual Daily Broadcast**: Two scheduled editions — morning official TRM (7:00 AM COT) and market close spot rate (1:15 PM COT).
- **Automated Scraper**: Official API consumers for both `datos.gov.co` (SuperFinanciera) and `proxy.icap.com.co` (SET-ICAP), with exponential backoff retry.
- **Financial Intelligence**: Dynamic message formatting computes rate changes with emojis (📈/📉/➖) and exact delta values for both editions.
- **Independent Deduplication**: Each edition guards against double-posting with its own state file, so a morning send never blocks the 1 PM close.
- **Direct Browser Broadcast**: Uses **Playwright** to natively type and send messages on WhatsApp Web — no Meta API or business account needed.
- **Weekday Scheduling**: Runs Monday–Friday only, preserving compute resources on non-trading days.
- **Self-Healing Interaction**: Uses Playwright **Locators** to automatically recover if the DOM re-renders during slow cloud syncs.
- **Zero-Cost**: Runs entirely on a GCP "Always Free" e2-micro instance.
- **Diagnostic-First**: Includes robust remote logging and failure-screenshot sync tools.

## ✨ Spotlight: Friday Weekly Summary
Every Friday morning, the bot gives the crew a compact market check-in alongside the regular TRM:

> 📊 *Resumen Semanal TRM*
> 🔹 Máximo semana: $3,349.63 COP
> 🔹 Mínimo semana: $3,208.66 COP
> 📈 Variación semanal: +$140.97 (4.39%)

A weekly snapshot built from the last 7 trading days, without disturbing the normal daily broadcast. Small, useful, and just a bit adorable.

## ✨ Spotlight: Market Close Broadcast *(new in v1.3.0)*
Every weekday at 1:15 PM COT, a second message delivers the official SET-FX spot market close snapshot:

> 📉 *Cierre Mercado USD/COP - 2026-10-22*
>
> 💵 Cierre: $3,191.20 COP (-0.06% vs apertura)
> 🔼 Máximo: $3,193.00 COP
> 🔽 Mínimo: $3,171.00 COP
> 📊 Apertura: $3,193.00 COP
>
> Fuente: SET-ICAP (proxy.icap.com.co)

Sourced from the official SET-ICAP public API — the same data feed used by Colombian market professionals. A clean end-of-morning-session pulse: where did the peso land, and how wide was today's spread?

## 📁 Project Documentation
For detailed guides on specific modules, refer to:
| Document | Purpose |
| :--- | :--- |
| [GCP_SETUP.md](docs/GCP_SETUP.md) | How to provision a $0.00/mo server in the Google Free Tier. |
| [CRON_SETUP.md](docs/CRON_SETUP.md) | How to schedule both daily runs on a Linux server. |
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

3. **Local Dry-Run (both editions)**:
   ```bash
   python main.py --edition morning --dry-run
   python main.py --edition closing --dry-run
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

### 3. Cloud Execution
On your Linux instance, the runner handles the virtual display and logging for either edition:
```bash
bash scripts/run_vm.sh --edition morning   # 7:00 AM COT
bash scripts/run_vm.sh --edition closing   # 1:15 PM COT
```

### 4. Dual Cron Schedule
See [CRON_SETUP.md](docs/CRON_SETUP.md) for the full dual-cron setup. The two entries are:
```cron
0 12 * * 1-5  cd ~/wa_trm_notifier && bash scripts/run_vm.sh --edition morning
15 18 * * 1-5 cd ~/wa_trm_notifier && bash scripts/run_vm.sh --edition closing
```

### 5. Monitoring & Diagnostics
If a cloud run fails or times out, pull the remote evidence to your local machine for analysis:
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
- ✅ Phase 5: Live Support & Stability — Complete
- ✅ Phase 6: Financial Intelligence — Complete
- ✅ Phase 7: Dual Broadcast (v1.3.0) — Released

### Phase 5 — Live Support Model
Post-deployment reliability work is managed in **time-boxed sprints** rather than monolithic planning cycles. Each sprint targets specific bugs or improvements surfaced from autonomous CRON runs.

| Artifact | Purpose |
| :--- | :--- |
| [BUGS.md](.gsd/phases/5/BUGS.md) | Active bug tracker — every bug linked to a release tag |
| [SPRINT.md](.gsd/SPRINT.md) | Current sprint scope and task status |
| [CHANGELOG.md](CHANGELOG.md) | Release history — every fix referenced by `BUG-NNN` ID |

> **Current version**: `v1.3.0` — Dual Broadcast (Morning TRM & Market Close Spot)

---
*Built with the **Get Shit Done (GSD)** methodology.*
