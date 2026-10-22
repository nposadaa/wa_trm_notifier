#!/bin/bash

# run_vm.sh — Memory-Safe execution for TRM Notifier on 1GB RAM VM
#
# Usage:
#   bash scripts/run_vm.sh                        # morning edition (default)
#   bash scripts/run_vm.sh --edition morning      # explicit morning
#   bash scripts/run_vm.sh --edition closing      # market close edition
#
# All arguments are forwarded directly to main.py, so --force, --dry-run,
# --headless, etc. all work as normal.

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"
mkdir -p logs

# 1. ENSURE 4GB SWAP (Critical for stability)
# Only run if swap is less than 3GB
SWAP_SIZE=$(free -m | grep -i swap | awk '{print $2}')
if [ "$SWAP_SIZE" -lt 3000 ]; then
    echo "⚠️  LOW SWAP DETECTED ($SWAP_SIZE MB). Increasing to 4GB..."
    sudo swapoff -a
    sudo rm -f /swapfile
    sudo fallocate -l 4G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    echo "✅ Swap increased to 4GB."
fi

# 2. Activate venv
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "Error: venv/bin/activate not found."
    exit 1
fi

# 3. Clean up
rm -f qr.png error_page.png
# Kill any lingering Xvfb or Chrome processes to free RAM
pkill -f Xvfb || true
pkill -f chromium || true
sudo rm -f /tmp/.X99-lock || true

# 4. Detect edition label for logging (cosmetic only — main.py enforces logic)
EDITION_LABEL="morning"
for arg in "$@"; do
    if [ "$arg" = "closing" ]; then
        EDITION_LABEL="closing"
        break
    fi
done

# 5. Run Synchronously (Foreground)
echo "------------------------------------------------"
echo "🚀 Starting TRM Notifier [${EDITION_LABEL^^} edition]..."
echo "------------------------------------------------"

export PYTHONUNBUFFERED=1
echo "" >> logs/vm_run.log
echo "==========================================================" >> logs/vm_run.log
echo "🚀 RUN START [${EDITION_LABEL^^}]: $(date -u '+%Y-%m-%d %H:%M:%S UTC')" >> logs/vm_run.log
echo "==========================================================" >> logs/vm_run.log
xvfb-run --server-args="-screen 0 1280x1024x24" python3 main.py --headless "$@" 2>&1 | tee -a logs/vm_run.log

echo "------------------------------------------------"
echo "✅ Execution completed. Check output above or in logs/vm_run.log"
echo "------------------------------------------------"
