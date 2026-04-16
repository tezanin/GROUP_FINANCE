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

$containerName = "group_finance-db-1"
$containerPath = "/tmp/group_finance_restore.dump"

Write-Host "Copying dump to container..."
docker cp $BackupFile "${containerName}:$containerPath"

Write-Host "Restoring database from dump..."
docker compose exec db pg_restore -U group_finance -d group_finance --clean --if-exists $containerPath

Write-Host "Restore completed successfully."