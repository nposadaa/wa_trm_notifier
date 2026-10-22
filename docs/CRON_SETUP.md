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

You can configure crontab using either **Method A (Interactive via Nano)** or **Method B (One-Click Command Line)**.

---

### Method A: Interactive Editor (`nano`)

1. **Open the crontab editor:**
   ```bash
   crontab -e
   ```
   *(If prompted to choose an editor for the first time, select `nano` by pressing `1` and `Enter`.)*

2. **Delete existing / old lines:**
   - Use the arrow keys to place your cursor on any previous TRM notifier line.
   - Press **`Ctrl + K`** (Cut/Delete line) to remove the entire line.
   - Repeat **`Ctrl + K`** for each old or comment line until all previous TRM configuration lines are cleared.

3. **Add the new dual-broadcast schedule:**
   - Move the cursor to the bottom of the file (or an empty line).
   - Copy the block below and paste it into the terminal (in Windows PowerShell SSH or browser SSH, **Right-Click** or press **`Ctrl + Shift + V`**):

   ```cron
   # TRM Notifier — Dual Daily Broadcast
   # Morning TRM (7:00 AM COT = 12:00 UTC) — Monday through Friday
   0 12 * * 1-5 cd /home/nposadaa111/wa_trm_notifier && bash scripts/run_vm.sh --edition morning

   # Market Close Spot (1:15 PM COT = 18:15 UTC) — Monday through Friday
   15 18 * * 1-5 cd /home/nposadaa111/wa_trm_notifier && bash scripts/run_vm.sh --edition closing
   ```

4. **Save and exit:**
   - Press **`Ctrl + O`** (Write Out / Save).
   - Press **`Enter`** to confirm the destination filename.
   - Press **`Ctrl + X`** to exit the editor.

   The terminal will output: `crontab: installing new crontab`.

---

### Method B: One-Liner (Automatic Clean & Install — Recommended)

If you prefer to avoid manual text editing, paste and run this single command directly in your VM terminal. It automatically removes any previous `wa_trm_notifier` entries and installs the clean dual schedule:

```bash
(crontab -l 2>/dev/null | grep -v 'wa_trm_notifier' | grep -v 'TRM Notifier'; cat << 'EOF'
# TRM Notifier — Dual Daily Broadcast
# Morning TRM (7:00 AM COT = 12:00 UTC) — Monday through Friday
0 12 * * 1-5 cd /home/nposadaa111/wa_trm_notifier && bash scripts/run_vm.sh --edition morning

# Market Close Spot (1:15 PM COT = 18:15 UTC) — Monday through Friday
15 18 * * 1-5 cd /home/nposadaa111/wa_trm_notifier && bash scripts/run_vm.sh --edition closing
EOF
) | crontab -
```

---

> **⚠️ Timezone Reminder:** GCP VMs run on UTC. COT is UTC−5.
> - 7:00 AM COT → **12:00 UTC**
> - 1:15 PM COT → **18:15 UTC**

---

## 3. Verify the Schedule

Run:
```bash
crontab -l
```

You should see both lines cleanly installed:
```text
# TRM Notifier — Dual Daily Broadcast
# Morning TRM (7:00 AM COT = 12:00 UTC) — Monday through Friday
0 12 * * 1-5 cd /home/nposadaa111/wa_trm_notifier && bash scripts/run_vm.sh --edition morning

# Market Close Spot (1:15 PM COT = 18:15 UTC) — Monday through Friday
15 18 * * 1-5 cd /home/nposadaa111/wa_trm_notifier && bash scripts/run_vm.sh --edition closing
```

If you see `no crontab for [user]` or old lines remain, repeat step 2.

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
