from django.db import migrations


def populate_company_codes(apps, schema_editor):
    """
    Заполняет поле `code` у всех существующих компаний,
    у которых оно пустое.
    Использует тот же генератор, что и CodeMixin.
    """
    from group_finance.apps.core.utils.code_generator import generate_unique_code

    Company = apps.get_model('org', 'Company')

    for company in Company.objects.filter(code__isnull=True):
        company.code = generate_unique_code(
            model_class=Company,
            name=company.name,
            instance_pk=company.pk,
        )
        company.save()


def reverse_populate_company_codes(apps, schema_editor):
    """
    Обратная операция — обнулить все коды.
    Нужна для миграции в обратную сторону (unmigrate).
    """
    Company = apps.get_model('org', 'Company')
    Company.objects.update(code=None)


class Migration(migrations.Migration):

    dependencies = [
        ('org', '0005_company_code'),
    ]

    operations = [
        migrations.RunPython(
            populate_company_codes,
            reverse_code=reverse_populate_company_codes,
        ),
    ]
