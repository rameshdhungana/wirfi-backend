# Generated by Django 2.0.7 on 2018-08-15 09:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wirfi_app', '0003_auto_20180814_0610'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='billing',
            name='stripe_token',
        ),
    ]
