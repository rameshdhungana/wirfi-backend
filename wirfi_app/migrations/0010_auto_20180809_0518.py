# Generated by Django 2.0.7 on 2018-08-09 05:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wirfi_app', '0009_auto_20180808_1037'),
    ]

    operations = [
        migrations.RenameField(
            model_name='device',
            old_name='location_photo',
            new_name='machine_photo',
        ),
    ]
