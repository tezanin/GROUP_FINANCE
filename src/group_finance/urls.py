from django.contrib import admin
from django.http import JsonResponse
from django.urls import path


def healthcheck(_request):
    return JsonResponse({"status": "ok", "service": "group_finance"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", healthcheck, name="healthcheck"),
]

