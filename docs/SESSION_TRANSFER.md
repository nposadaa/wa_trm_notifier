# WhatsApp Cloud Session Transfer Guide

Due to Meta's aggressive security algorithms, running a headless WhatsApp Web instance on a cloud VM can sometimes result in a flagged/invalidated session token (especially if the browser is forcefully killed multiple times during testing). When this happens, the script will loop infinitely on the `SPLASH` screen with `400 Bad Request` or `aquire-persistent-storage-denied` errors.

To bypass this without needing a graphical interface on the VM, we use the **Local-to-Cloud Transfer** method.

---

## Part 1: Local Terminal (Your Laptop)

These steps will generate a fresh, cryptographically valid session token using your local browser and your phone.

1. **Open your local terminal** (PowerShell, Command Prompt, or Bash) and navigate to the project directory:
   ```bash
   cd path/to/wa_trm_notifier
   ```

2. **Delete any broken local session** so we start completely clean:
   - *Windows (PowerShell)*: `Remove-Item -Recurse -Force whatsapp_session`
   - *Mac/Linux*: `rm -rf whatsapp_session`

3. **Run the script locally in visual mode**:
   ```bash
   python main.py
   ```
   *A visible Chromium browser will open. Scan the QR code with your phone. Wait completely until your chats load and the "WhatsApp" interface is fully visible.*

4. **Close cleanly**:
   Once you see the green "Task completed successfully" in your terminal, the browser will close automatically. Do **not** forcefully close the terminal early, as this corrupts the SQLite databases.

5. **Zip the new session folder**:
   - *Windows (PowerShell)*: `Compress-Archive -Path "whatsapp_session" -DestinationPath "session.zip" -Force`
   - *Mac/Linux*: `zip -r session.zip whatsapp_session`

6. **Upload to GCP VM**:
   Use `gcloud`, SFTP, or the Google Cloud SSH web interface to upload `session.zip` to the `/home/[your-user]/wa_trm_notifier/` directory on your VM.
   *(Example using gcloud)*:
   ```bash
   gcloud compute scp session.zip [USERNAME]@[VM-NAME]:~/wa_trm_notifier/
   ```

---

## Part 2: GCP VM Terminal (The Server)

These steps will unpack the authorized tokens onto your remote server.

1. **SSH into your VM** and navigate to your project:
   ```bash
   cd ~/wa_trm_notifier
   ```

2. **Kill any zombie processes and delete the dead session folder**:
   ```bash
   pkill -f Xvfb || true
   pkill -f chromium || true
   rm -rf whatsapp_session
   ```

3. **Unzip the fresh session**:
   ```bash
   unzip session.zip
   ```

4. **(Optional) Clean up the zip file** so no sensitive keys sit in your filesystem forever:
   ```bash
   rm session.zip
   ```

5. **Run the headless execution test**:
   ```bash
   source venv/bin/activate
   xvfb-run --server-args="-screen 0 1024x768x24" python3 main.py --headless
   ```

If successful, the script will successfully recognize the `LOGGED_IN` state in about 20-30 seconds, bypass the QR code, and send the messages.
