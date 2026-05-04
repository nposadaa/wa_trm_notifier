# Automated Cron Task Scheduling (GCP VM)

Once your application is fully stabilized via the session transfer, you should set up a `cron` job on your server to autonomously execute the broadcaster every day.

## 1. The Standard Runner
To ensure the environment, virtual display (`xvfb`), and logging are handled correctly, this project uses a standard runner script: **`scripts/run_vm.sh`**.

This script:
1. Navigates to the project root.
2. Activates the Python virtual environment.
3. Launches a virtual X-server (required for WhatsApp Web).
4. Executes `main.py` and captures all output to `logs/vm_run.log`.

## 2. Configuring Crontab
Open the cron editor on the VM:
```bash
crontab -e
```
*(If prompted to choose an editor, select `nano` by pressing '1'.)*

Scroll to the very bottom to add your schedule.

### Schedule Formatting
Cron schedules use 5 asterisks: `Minute Hour Day Month DayOfWeek`.

**Warning on Timezones:** GCP VM servers typically operate on **UTC** time. If you want the script to run at **7:00 AM (Colombia Time / UTC-5)**, you must schedule it for **12:00 PM (UTC)**.

To schedule the script for weekdays only (Monday through Friday) at 12:00 (UTC), use `1-5` for the DayOfWeek field:
```bash
0 12 * * 1-5 cd /home/nposadaa111/wa_trm_notifier && bash scripts/run_vm.sh
```

Save and exit using the following **Nano** shortcuts:
1. **Press `Ctrl + O`** then **`Enter`** to save (Write Out).
2. **Press `Ctrl + X`** to exit.

The terminal will display `crontab: installing new crontab`. The cron daemon will then pick up the new job and run the script daily in the background.

## 3. Monitoring the System (Local Machine)
You no longer need to check logs manually on the VM. Use the diagnostic utility from your **Local PowerShell** terminal:

```powershell
# Pull latest logs and screenshots from the VM
.\scripts\fetch-logs.ps1
```

### What to check in the logs:
- **`logs/vm_run.log`**: Shows the high-level execution and any `xvfb` errors.
- **`logs/notifier_[date].log`**: Contains the detailed broadcaster logs, including the "Sync Progress" and delivery verification.
- **`error_page.png`**: If a timeout occurs, this screenshot shows the exact browser state.

## 4. Manual Troubleshooting
If the cron job fails to send (e.g., due to a session expiration), you will see "QR Required" in the logs. In this case:
1. Delete the remote session: `rm -rf ~/wa_trm_notifier/whatsapp_session`
2. Generate a new session locally.
3. Transfer the new `whatsapp_session.zip` to the VM.

## 5. Verification
To verify that your schedule was saved correctly, run the **List** command on your VM:
```bash
crontab -l
```
Standard output will show your scheduled command at the bottom of the file. If you see the message `no crontab for [user]`, the save was not successful.
