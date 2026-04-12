# fetch-logs.ps1 — Automated GCP Log Sync
# Usage: .\scripts\fetch-logs.ps1

$VM_NAME = "trm-notifier"
$ZONE = "us-central1-a"
$REMOTE_USER = "nposadaa111"
$REMOTE_PATH = "/home/nposadaa111/wa_trm_notifier"

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "   CLOUD SYNC: DIAGNOSTICS FROM GCP ($VM_NAME)" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan

# 1. Ensure local logs dir exists
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}

# 2. Sync Logs
Write-Host "[1/2] Syncing remote logs to .\logs\..." -ForegroundColor Gray
gcloud compute scp --recurse "${REMOTE_USER}@${VM_NAME}:${REMOTE_PATH}/logs/*" ".\logs\" --zone=$ZONE
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to sync logs. Ensure gcloud is authenticated and VM is RUNNING."
    exit $LASTEXITCODE
}

# 3. Sync Screenshots
Write-Host "[2/2] Syncing remote screenshots..." -ForegroundColor Gray
gcloud compute scp "${REMOTE_USER}@${VM_NAME}:${REMOTE_PATH}/*.png" "." --zone=$ZONE --quiet 2>$null

Write-Host "✅ Sync Complete." -ForegroundColor Green
Write-Host ""

# 4. Display Tail of Most Recent Log
$LatestLog = Get-ChildItem -Path "logs" -Filter "notifier_*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$VMRunLog = Get-Item -Path "logs/vm_run.log" -ErrorAction SilentlyContinue

if ($LatestLog) {
    Write-Host "--- Tail of Latest Notifier Log ($($LatestLog.Name)) ---" -ForegroundColor Yellow
    Get-Content $LatestLog.FullName -Tail 20
}

if ($VMRunLog) {
    Write-Host "`n--- Tail of VM Runner Log (vm_run.log) ---" -ForegroundColor Yellow
    Get-Content $VMRunLog.FullName -Tail 20
}

Write-Host "`n=====================================================" -ForegroundColor Cyan
