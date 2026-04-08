# WhatsApp Cloud Session Transfer Guide

Due to Chromium's Operating System-level cryptography (Windows uses DPAPI, Linux uses libsecret/GNOME), you **cannot** generate a Playwright session block on a Windows computer and zip it to a Linux Server. The server will fail to decrypt the stored IndexedDB and Cookie secrets and immediately trap itself in a 400 Bad Request / "Storage Persistence Denied" death loop. 

To bypass this without a graphic interface on the VM, we run the authenticator headlessly on the VM, download the exact QR code screenshot image back to your laptop, and scan it from your screen!

---

## The Secure Authentication Flow 

### 1. Run the Authenticator on the VM
Instead of transferring the session folder from your local laptop, **SSH into your VM** and let the Linux machine generate its own session:

```bash
cd ~/wa_trm_notifier
source venv/bin/activate
```

Kill any zombie processes and delete the dead/Windows-transferred session folder so we start entirely clean:
```bash
pkill -f Xvfb || true; pkill -f chromium || true
sudo rm -rf whatsapp_session
sudo rm qr.png
```

Launch the Authenticator Tunnel explicitly in headless mode:
```bash
xvfb-run --server-args="-screen 0 1024x768x24" python3 auth.py --headless
```

*The terminal will output: `!!! qr.png HAS BEEN SAVED TO VM. PLEASE DOWNLOAD IT NOW TO SCAN !!!` and pause.*

### 2. Download the QR Code 
**Open a SECOND terminal window on your local Windows laptop** (do not close the SSH one) and use `gcloud` to securely pull the `qr.png` file from the VM to your laptop:

```bash
gcloud compute scp nposadaa111@trm-notifier:/home/nposadaa111/wa_trm_notifier/qr.png .
```

### 3. Scan the Screenshot
Open the downloaded `qr.png` image on your Windows computer and scan it with WhatsApp on your phone.

### 4. Wait for Stabilization
Switch back to your SSH terminal. Within a few seconds of scanning, the script will notice the change, save the `LOGGED_IN` status natively using Linux cryptography, and elegantly close:

```text
✅ Session successfully synchronized!
Closing browser cleanly...
Session directory is safe to zip and transfer!
```

**You are fully production-ready.** The `whatsapp_session` folder existing on the Linux VM is completely native and fully hardened. The cron job will now run flawlessly without any 400 rejection errors.
