# GCP VM Setup — TRM Notifier

## Step 1: Create VM

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Navigate: ☰ Menu → **Compute Engine** → **VM Instances**
3. If first time: enable Compute Engine API (takes ~1 min)
4. Click **Create Instance**
5. Configure:

| Setting | Value |
|---------|-------|
| **Name** | `trm-notifier` |
| **Region** | `us-central1` (Iowa) — free tier eligible |
| **Zone** | `us-central1-a` |
| **Machine type** | `e2-micro` (2 vCPU, 1 GB) |
| **Boot disk** | Click **Change** → Ubuntu 22.04 LTS, **x86/64 amd64** (NOT Minimal, NOT Arm64), 30 GB standard |
| **Firewall** | Check "Allow HTTP" (not strictly needed but useful) |

6. Expand **Advanced options** → **Networking** → ensure external IP = **Ephemeral** (default)
7. Click **Create**

> **IMPORTANT**: Only `e2-micro` in `us-west1`, `us-central1`, or `us-east1` is free.

---

## Step 2: SSH Into VM

Easiest way — use browser SSH:
1. In VM instances list, click **SSH** button on your VM row
2. Browser terminal opens directly — no keys needed

Or from local PowerShell:
```powershell
gcloud compute ssh trm-notifier --zone=us-central1-a
```
(Requires gcloud CLI installed)

---

## Step 3: Server Setup (run these on VM)

Copy-paste this entire block:

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install dependencies
sudo apt install -y python3-pip python3-venv xvfb git

# 3. Create swap file (critical for 1GB RAM)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 4. Verify swap
free -h

# 5. Clone repo
cd ~
git clone https://github.com/nposadaa/wa_trm_notifier.git
cd wa_trm_notifier

# 6. Setup Python env
python3 -m venv venv
source venv/bin/activate

# 7. Install Python deps
pip install -r requirements.txt

# 8. Install Playwright + browser
playwright install chromium
playwright install-deps
```

---

## Step 4: Run & Activate (The QR Scan)

To get things running and logged in:

1. **Wait for login**:
   Make sure you are in the project folder and the venv is active:
   ```bash
   cd ~/wa_trm_notifier
   chmod +x scripts/run_vm.sh
   ./scripts/run_vm.sh
   ```

2. **Wait for "LOGIN REQUIRED"**:
   - Open a **NEW PowerShell/Terminal** on your **LOCAL computer**.
   - Run the command to copy the QR code from the VM to your laptop:
     ```powershell
     gcloud compute scp trm-notifier:~/wa_trm_notifier/qr.png . --zone=us-central1-a
     ```
   - Open `qr.png` on your computer and scan it with your phone (WhatsApp → Linked Devices).

3. **Verify Success**:
   - Once scanned, the script on the VM should complete automatically and send the TRM message.

---

## Step 5: Automation (Cron)

Schedule the daily broadcast (7:00 AM COT = 12:00 UTC, Weekdays):
1. Run `crontab -e` on the VM.
2. Add this line:
   ```cron
   0 12 * * 1-5 /usr/bin/xvfb-run --server-args="-screen 0 1280x1024x24" /home/$USER/wa_trm_notifier/venv/bin/python3 /home/$USER/wa_trm_notifier/main.py --headless >> /home/$USER/wa_trm_notifier/logs/cron.log 2>&1
   ```
