# Automated Cron Task Scheduling (GCP VM)

This project runs **two daily WhatsApp broadcasts** via `cron` on your GCP VM:

| Edition | Time (COT) | Time (UTC) | Cron flag |
|---------|-----------|-----------|-----------|
| **Morning TRM** | 7:00 AM Mon–Fri | 12:00 UTC | `--edition morning` |
| **Market Close Spot** | 1:15 PM Mon–Fri | 18:15 UTC | `--edition closing` |

> **Why 1:15 PM?** SET-ICAP publishes the official 1:00 PM close snapshot with a ~10–15 min delay. 1:15 PM COT (18:15 UTC) is the reliable earliest pickup time.

---

## 1. The Standard Runner

Both editions use the same script: **`scripts/run_vm.sh`**.

The script:
1. Navigates to the project root.
2. Ensures sufficient swap memory (4 GB) for Chromium stability.
3. Activates the Python virtual environment.
4. Kills any stale Xvfb / Chromium processes.
5. Launches a virtual X-server and executes `main.py --headless` with all passed flags.
6. Appends all output to `logs/vm_run.log`.

---

## 2. Configuring Crontab

Open the cron editor on the VM:
```bash
crontab -e
```
*(If prompted to choose an editor, select `nano` by pressing '1'.)*

### Dual-Broadcast Schedule

Paste **both lines** at the bottom of the file:

```bash
# TRM Notifier — Dual Daily Broadcast
# Morning TRM (7:00 AM COT = 12:00 UTC) — Monday through Friday
0 12 * * 1-5 cd /home/nposadaa111/wa_trm_notifier && bash scripts/run_vm.sh --edition morning

# Market Close Spot (1:15 PM COT = 18:15 UTC) — Monday through Friday
15 18 * * 1-5 cd /home/nposadaa111/wa_trm_notifier && bash scripts/run_vm.sh --edition closing
```

> **⚠️ Timezone:** GCP VMs run on UTC. COT is UTC−5.
> - 7:00 AM COT → **12:00 UTC**
> - 1:15 PM COT → **18:15 UTC**

Save and exit using these **Nano** shortcuts:
1. **`Ctrl + O`** then **`Enter`** — save (Write Out).
2. **`Ctrl + X`** — exit.

The terminal will display `crontab: installing new crontab`.

---

## 3. Verify the Schedule

```bash
crontab -l
```

You should see both lines at the bottom. If you see `no crontab for [user]`, the save was not successful — repeat step 2.

---

## 4. Monitoring the System (Local Machine)

Pull logs and screenshots from the VM to your Windows machine:

```powershell
# Pull latest logs and screenshots from the VM
.\scripts\fetch-logs.ps1
```

### What to check in the logs

| File | What it shows |
|------|--------------|
| `logs/vm_run.log` | High-level run log; shows edition label, start/end timestamps, xvfb errors |
| `logs/notifier_[date].log` | Detailed broadcaster log — scrape values, message text, delivery verification |
| `error_page.png` | Browser screenshot captured on timeout — shows exact WhatsApp state |

### Deduplication state files

Each edition writes its own guard file to prevent double-posting:

| File | Edition |
|------|---------|
| `.gsd/last_success_morning.date` | Morning TRM |
| `.gsd/last_success_closing.date` | Market Close |
| `.gsd/last_success.date` | Legacy alias (kept in sync with morning) |

---

## 5. Manual Execution

Run either edition by hand from the VM for testing or recovery:

```bash
# Morning edition (dry-run, no WhatsApp send)
bash scripts/run_vm.sh --edition morning --dry-run

# Closing edition (dry-run)
bash scripts/run_vm.sh --edition closing --dry-run

# Force a re-send even if already sent today
bash scripts/run_vm.sh --edition morning --force
bash scripts/run_vm.sh --edition closing --force
```

---

## 6. Troubleshooting

### WhatsApp session expired (QR code required)
You will see `QR Required` or a clock-icon stall in the logs. Fix:
1. Delete the remote session: `rm -rf ~/wa_trm_notifier/whatsapp_session`
2. [Re-authenticate locally](SESSION_TRANSFER.md) and transfer the new `whatsapp_session.zip`.

### Only one edition ran
Check the dedup files — if `.gsd/last_success_morning.date` and `.gsd/last_success_closing.date` both already contain today's date, both will skip. Use `--force` to override.

### SET-ICAP API down
The closing edition will log `Error scraping spot market` and send a ⚠️ system alert via WhatsApp. No action needed — it retries on the next cron trigger.
