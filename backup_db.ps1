$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

$backupDir = Join-Path $projectRoot "backups"
if (!(Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir | Out-Null
}

$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"

$sqlFile = Join-Path $backupDir "group_finance_$timestamp.sql"
$dumpFile = Join-Path $backupDir "group_finance_$timestamp.dump"

Write-Host "Creating SQL backup: $sqlFile"
docker compose exec -T db pg_dump -U group_finance -d group_finance > $sqlFile

Write-Host "Creating custom dump backup: $dumpFile"
docker compose exec -T db pg_dump -U group_finance -d group_finance -Fc > $dumpFile

Write-Host "Backup completed successfully."
Write-Host "SQL : $sqlFile"
Write-Host "DUMP: $dumpFile"