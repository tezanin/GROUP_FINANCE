import importlib

from django.apps import apps

mod = importlib.import_module(
    "group_finance.apps.banking.migrations.0003_backfill_amount_rub"
)

mod.backfill_amount_rub(apps, None)
