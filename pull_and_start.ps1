Write-Host "=== Обновление проекта и запуск ===" -ForegroundColor Cyan

if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "Ошибка: файл docker-compose.yml не найден. Запусти скрипт из корня проекта." -ForegroundColor Red
    exit 1
}

Write-Host "`n[1/4] Проверяю Docker..." -ForegroundColor Yellow
docker info | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker Desktop не запущен. Сначала открой Docker Desktop, потом повтори." -ForegroundColor Red
    exit 1
}

Write-Host "[2/4] Получаю изменения из GitHub..." -ForegroundColor Yellow
git pull
if ($LASTEXITCODE -ne 0) {
    Write-Host "git pull завершился с ошибкой. Проверь статус репозитория." -ForegroundColor Red
    exit 1
}

Write-Host "[3/4] Поднимаю контейнеры..." -ForegroundColor Yellow
docker compose up --build -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "Не удалось запустить контейнеры." -ForegroundColor Red
    exit 1
}

Write-Host "[4/4] Показываю статус контейнеров..." -ForegroundColor Yellow
docker compose ps

Write-Host "`nГотово. Проект обновлен и запущен." -ForegroundColor Green
Write-Host "Если это первый запуск на новой базе, выполни еще: .\migrate.ps1" -ForegroundColor Cyan
