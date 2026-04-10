# WhatsApp Cloud Session Transfer Guide

By default, Chromium encrypts its IndexedDB and LocalStorage using the host Operating System's native keychain (e.g., DPAPI on Windows, libsecret on Linux). To prevent our session from becoming locked to a specific OS, our `browser_config.py` forcefully uses `--password-store=basic` and `--use-mock-keychain`. 

This unlocks true portability, allowing us to perform the heavy initial E2E sync on a powerful local machine, and then "Zip and Ship" it safely to a lightweight headless cloud server!

---

## The "Zip and Ship" Authentication Flow 

### 1. Execute Local Authenticator (Windows)
Run the authenticator locally on your Windows machine to leverage its RAM for the heavy E2E key decryption:

```powershell
# In PowerShell:
Remove-Item -Recurse -Force whatsapp_session -ErrorAction SilentlyContinue
.\venv\Scripts\python.exe auth.py
```
* **Scan the QR Code** with your phone.
* **Wait patiently** until your phone's Linked Devices menu officially changes from "Syncing" to **"Active"**.
* Press `ENTER` to safely close the browser and flush the complete database to disk.

### 2. Zip the Session
Package the stabilized folder into a lightweight zip:

```powershell
Compress-Archive -Path whatsapp_session -DestinationPath whatsapp_session.zip -Force
```

### 3. Transfer to Cloud
Upload the zip to your Linux VM using Google Cloud's secure copy:

```powershell
gcloud compute scp whatsapp_session.zip YOUR_VM_USERNAME@YOUR_VM_NAME:/home/YOUR_VM_USERNAME/wa_trm_notifier/
```
*(If the folder path varies, simply uploading it to your home root `/home/YOUR_VM_USERNAME/` and moving it later is fine).*

### 4. Unpack and Secure on Server
Log into your VM via SSH, navigate to your `wa_trm_notifier` directory, and cleanly extract the session. **Crucially, re-apply write permissions** to prevent Linux from restricting the Windows-created files:

```bash
# Inside the VM:
rm -rf whatsapp_session
unzip -q whatsapp_session.zip
chmod -R 777 whatsapp_session/
```

### 5. Run the Broadcaster
With the mocked headless storage configs ensuring WhatsApp doesn't throw a `persistence denied` exception on headless Chromium, you can now run the standard execution script flawlessly:

```bash
bash scripts/run_vm.sh
```
