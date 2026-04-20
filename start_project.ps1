Write-Host "=== Запуск проекта ===" -ForegroundColor Cyan

docker info > $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker не запущен. Открой Docker Desktop." -ForegroundColor Red
    exit 1
}

docker compose up --build -d

Write-Host "Проект запущен " -ForegroundColor Green