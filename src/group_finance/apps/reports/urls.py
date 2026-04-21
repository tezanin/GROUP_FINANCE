from django.urls import path

from . import views


app_name = "reports"

urlpatterns = [
    path("cashflow/", views.cashflow_report, name="cashflow"),
]
