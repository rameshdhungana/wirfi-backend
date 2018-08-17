# Generated by Django 2.0.7 on 2018-08-10 08:27

from django.db import migrations


def create_site(apps, schema_editor):
    from django.contrib.sites.models import Site

    Site.objects.all().delete()
    Site.objects.create(name="wirfi.testiw.codesamaj.com", domain="wirfi.testiw.codesamaj.com")


class Migration(migrations.Migration):

    dependencies = [
        ('wirfi_app', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_site),
    ]