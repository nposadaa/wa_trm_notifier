# GCP VM Setup — TRM Notifier

## Step 1: Create VM
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. **Compute Engine** → **VM Instances** → **Create Instance**
3. Configure:
   - **Machine type**: `e2-micro` (Free tier)
   - **Boot disk**: Ubuntu 22.04 LTS (30 GB)
   - **Zone**: `us-central1-a` (or any free tier zone)

## Step 2: Server Setup (Run on VM)
```bash
sudo apt update && sudo apt install -y python3-pip python3-venv xvfb git
# Create 4GB Swap (MANDATORY for stability)
sudo fallocate -l 4G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Setup Project
git clone https://github.com/nposadaa/wa_trm_notifier.git ~/wa_trm_notifier
cd ~/wa_trm_notifier
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
playwright install chromium && playwright install-deps
```

## Step 3: Local-to-Cloud Session Transfer (THE STABLE METHOD)
Since cloud browsers are often blocked by WhatsApp during high-latency handshakes, we link the account locally and transfer the cryptokeys.

1. **On your Laptop**:
   - Run: `python3 main.py --discovery` (or use the one we already linked).
   - Once logged in, close the browser.
   - Zip the folder: `whatsapp_session/` -> `session.zip`.
2. **On the VM**:
   - Use the **Gear (⚙️) → Upload file** in the Browser SSH window.
   - Upload `session.zip` and `recipients.json`.
   - Move them: `mv ~/session.zip ~/recipients.json ~/wa_trm_notifier/`.
   - Unzip: `cd ~/wa_trm_notifier && unzip session.zip`.

## Step 4: Run & Verify
1. **Interactive Test**:
   ```bash
   cd ~/wa_trm_notifier && source venv/bin/activate
   xvfb-run --server-args="-screen 0 1280x800x24" python3 main.py --headless
   ```
2. **Success Check**: Look for `✅ SUCCESS: Sent message to...` in the terminal.

## Step 5: Automate (Cron)
Add this to your crontab (`crontab -e`):
```bash
0 7 * * * cd /home/nposadaa111/wa_trm_notifier && ./scripts/run_vm.sh
```
*Note: This runs daily at 7:00 AM local VM time.*
