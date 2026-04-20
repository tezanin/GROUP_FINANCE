Write-Host "=== Применение миграций ===" -ForegroundColor Cyan

docker compose exec web python manage.py migrate