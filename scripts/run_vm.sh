#!/bin/bash

# run_vm.sh — Easy execution for TRM Notifier on Headless VM

# 1. Path to the project
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# 2. Activate venv
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "Error: venv/bin/activate not found. Did you run the setup steps?"
    exit 1
fi

# 3. Clean old screenshots
rm -f qr.png error_page.png

# 4. Run with Xvfb and explicit screen settings
echo "Starting TRM Notifier in headless mode..."
xvfb-run --server-args="-screen 0 1280x1024x24" python3 main.py --headless "$@"

# 5. Check if QR was generated
if [ -f "qr.png" ]; then
    echo ""
    echo "------------------------------------------------"
    echo "⚠️  ACTION REQUIRED: WhatsApp QR Code Generated!"
    echo "------------------------------------------------"
    echo "To see the QR code, run this command on your LOCAL machine:"
    echo "gcloud compute scp trm-notifier:~/wa_trm_notifier/qr.png . --zone=us-central1-a"
    echo "------------------------------------------------"
fi
