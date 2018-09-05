# Generated by Django 2.0.7 on 2018-08-22 05:30

from django.db import migrations


def add_industry_type(apps, schema_editor):
    from wirfi_app.models import Industry

    Industry.objects.all().delete()
    Industry.objects.bulk_create([
        Industry(name="Digital Signage"),
        Industry(name="ATM"),
        Industry(name="Vending"),
        Industry(name="Check/Cashing"),
        Industry(name="MicroMarket/Mobile"),
    ])


class Migration(migrations.Migration):

    dependencies = [
        ('wirfi_app', '0011_industry'),
    ]

    operations = [
        migrations.RunPython(add_industry_type),
    ]