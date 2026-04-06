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

## Step 4: Run & Activate (Memory-Safe)

To prevent the VM from crashing due to low RAM (OOM), we now use a background execution script with resource blocking.

1.  **Sync & Start**:
    Ensure you are in the project folder and run the new helper script:
    ```bash
    cd ~/wa_trm_notifier
    git pull
    chmod +x scripts/run_vm.sh
    ./scripts/run_vm.sh
    ```
    *Note: This script will automatically increase your swap to 4GB if needed.*

2.  **Download the QR Code**:
    Since `gcloud` is not installed localy, use the Browser SSH features:
    - Click the **Gear icon (⚙️)** in the top-right of your Browser SSH window.
    - Select **Download file**.
    - Enter the path: `/home/nposadaa/wa_trm_notifier/qr.png`
    - Open the downloaded `qr.png` on your laptop and scan it.

3.  **Check Logs**:
    If it fails or you want to see what's happening in the background:
    ```bash
    tail -f logs/vm_run.log
    ```

---

## Step 5: Troubleshooting "Black Screenshots"

If you are still getting black screens or timeouts:
1.  **Check error_page.png**: Download `/home/nposadaa/wa_trm_notifier/error_page.png` via the same Gear icon method.
2.  **WhatsApp Structure**: If WhatsApp changed its layout, we may need to update the selectors in `broadcaster.py`.
3.  **Restart VM**: If the system is extremely sluggish, use the **RESET** button in the GCP Console.
