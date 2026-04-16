param(
    [Parameter(Mandatory=$true)]
    [string]$BackupFile
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

if (!(Test-Path $BackupFile)) {
    throw "Backup file not found: $BackupFile"
}

Write-Host "Restoring database from: $BackupFile"
Get-Content $BackupFile | docker compose exec -T db psql -U group_finance -d group_finance

Write-Host "Restore completed successfully."