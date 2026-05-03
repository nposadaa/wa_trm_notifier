# Oracle Cloud VM Setup — TRM Notifier

## Step 1: Create Account
1. Go to [cloud.oracle.com](https://cloud.oracle.com)
2. Click **Sign Up**
3. Enter email, name, country (Colombia)
4. Credit card needed for verification — **no charge**
5. Pick **Home Region** → closest to you (e.g. `Brazil East (Sao Paulo)` or `US East`)

> [!WARNING]
> Home Region **cannot be changed later**. Pick carefully. Some regions have capacity issues.

---

## Step 2: Create VM

1. Log into **Oracle Cloud Console**
2. Navigate: ☰ Menu → **Compute** → **Instances** → **Create Instance**
3. Configure:

| Setting | Value |
|---------|-------|
| **Name** | `trm-notifier` |
| **Image** | Ubuntu 22.04 (Canonical) |
| **Shape** | Ampere A1 Flex (ARM) |
| **OCPUs** | 1 (free allows up to 4) |
| **RAM** | 6 GB (free allows up to 24) |
| **Boot Volume** | 50 GB (default) |

4. **Networking**: Accept defaults (new VCN + public subnet)
5. **SSH Key**: Choose **Generate a key pair** → **Download both keys**
   - Save private key as `oracle_key.pem`
   - Save public key
6. Click **Create**

> [!IMPORTANT]
> If you see "Out of capacity" error, try:
> - Different availability domain (AD-2 or AD-3)
> - Reduce to 1 OCPU / 4 GB RAM
> - Try again in a few hours

---

## Step 3: SSH Into VM

Once instance shows **Running** (green), copy **Public IP Address**.

Open PowerShell:
```powershell
# Move key to safe location
Move-Item Downloads\oracle_key.pem ~\.ssh\oracle_key.pem

# Fix permissions (required)
icacls $HOME\.ssh\oracle_key.pem /reset
icacls $HOME\.ssh\oracle_key.pem /grant:r "$($env:USERNAME):(R)"
icacls $HOME\.ssh\oracle_key.pem /inheritance:r

# Connect
ssh -i ~/.ssh/oracle_key.pem ubuntu@<YOUR_PUBLIC_IP>
```

You should see: `ubuntu@trm-notifier:~$`

---

## Step 4: Tell Me When Done

Once you can SSH in, tell me **the public IP** and I will:
1. Give you exact commands to install Python, Playwright, Xvfb
2. Help transfer WhatsApp session
3. Set up cron job

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Out of capacity" | Try different region/AD, reduce specs |
| SSH timeout | Open port 22 in Security List (VCN → Subnet → Security List → Ingress Rules) |
| Permission denied | Check key path + permissions with `icacls` |
| Can't find Ampere A1 | Your region may not have ARM. Try AMD E2.1.Micro (1GB) |
