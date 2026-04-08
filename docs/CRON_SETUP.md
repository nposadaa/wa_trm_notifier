# Automated Cron Task Scheduling (GCP VM)

Once your application is fully stabilized via the session transfer, you should set up a `cron` job on your server to autonomously execute `main.py` every day.

## 1. Finding Your Execution Path
Cron environments do **not** automatically load your `.bashrc`, meaning standard variables like your Python virtual environment path or your `$PATH` will not exist. We must use absolute paths to invoke the scraper perfectly.

The two absolute paths we need:
1. The path to your virtual environment Python: `/home/[your-username]/wa_trm_notifier/venv/bin/python3`
2. The path to your `main.py` entrypoint: `/home/[your-username]/wa_trm_notifier/main.py`

## 2. Generating The Execution Shell Script
The safest way to run complex commands like `xvfb-run` inside cron is to wrap them in a small `.sh` file so the `$PATH` is contained.

On your VM, create a file named `run_notifier.sh` inside your project directory:
```bash
cd ~/wa_trm_notifier
nano run_notifier.sh
```

Paste the following execution sequence:
```bash
#!/bin/bash
cd /home/$USER/wa_trm_notifier

# Activate environment implicitly by calling the absolute binary path
# xvfb-run creates the virtual X.org headless server
/usr/bin/xvfb-run --server-args="-screen 0 1024x768x24" /home/$USER/wa_trm_notifier/venv/bin/python3 main.py --headless >> /home/$USER/wa_trm_notifier/cron_output.log 2>&1
```

Save the file and mark it as executable:
```bash
chmod +x run_notifier.sh
```

## 3. Configuring Crontab
Open the cron editor on the VM:
```bash
crontab -e
```
*(If prompted to choose an editor, select `nano` by pressing '1'.)*

Scroll to the very bottom to add your schedule.

### Schedule Formatting
Cron schedules use 5 asterisks: `Minute Hour Day Month DayOfWeek`.
**Warning on Timezones:** GCP VM servers typically operate on **UTC** time. If you want the script to run at **7:00 AM (Colombia Time / UTC-5)**, you must schedule it for **12:00 PM (UTC)**.

To schedule the script for every day at 12:00 (UTC):
```bash
0 12 * * * /home/nposadaa111/wa_trm_notifier/run_notifier.sh
```

Save and exit. The cron daemon will immediately pick up the new job and run the script daily invisibly in the background.

## 4. Monitoring the System
Because we explicitly piped all output, any errors (like a killed session) or successes will be saved directly.
To check the result of the last automated run:
```bash
cat ~/wa_trm_notifier/cron_output.log
```
