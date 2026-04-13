# GCP Always Free VM Setup Guide

This project is optimized to run on the **Google Cloud Platform (GCP) Always Free Tier**. Follow these instructions to provision a server that costs $0.00/month while providing 24/7 reliability.

---

## 1. Google Cloud "Always Free" Criteria
To ensure your VM remains free, you must select the specific configurations below:

- **Region**: `us-west1`, `us-central1`, or `us-east1`.
- **Machine Type**: `e2-micro` (2 vCPUs, 1 GB RAM).
- **Storage**: Up to 30 GB of Standard Persistent Disk.

> [!WARNING]
> Selecting other regions or machine types (like `f1-micro` or `e2-medium`) will accrue monthly charges.

---

## 2. Provisioning Steps

1. **Go to Google Cloud Console**: Navigate to the [Compute Engine > VM Instances](https://console.cloud.google.com/compute/instances) page.
2. **Create Instance**:
   - **Name**: `trm-notifier`
   - **Region**: `us-central1 (Iowa)`
   - **Machine Configuration**:
     - General-purpose > E2
     - Machine type: `e2-micro`
   - **Boot Disk**:
     - Operating System: `Ubuntu`
     - Version: `Ubuntu 22.04 LTS` (recommended)
     - Size: 20 GB
3. **Identity and API Access**:
   - Allow default access.
4. **Firewall**:
   - You **do not** need to allow HTTP/HTTPS traffic (this project only makes outbound requests).
5. **Click Create**.

---

## 3. Connecting to your VM

The easiest way to connect and manage your project is via the `gcloud` CLI from your local machine:

```powershell
# Authenticate with Google
gcloud auth login

# Connect via SSH
gcloud compute ssh [YOUR_USERNAME]@[INSTANCE_NAME] --zone [YOUR_ZONE]
```

---

## 4. Software Prerequisites (Inside VM)
Once connected, run this one-time setup to prepare the environment:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-venv xvfb libgbm-dev
```

This ensures the **Virtual X-Server (xvfb)** is available to handle the headless browser rendering required for WhatsApp.

---

## 5. Next Steps
Once your VM is running, proceed to the [CRON_SETUP.md](CRON_SETUP.md) guide to automate your daily broadcasts.
