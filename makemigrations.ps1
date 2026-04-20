Write-Host "=== Создание миграций ===" -ForegroundColor Cyan

docker compose exec web python manage.py makemigrations