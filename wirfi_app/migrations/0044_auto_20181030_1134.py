# Generated by Django 2.0.7 on 2018-10-30 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wirfi_app', '0043_auto_20181029_1211'),
    ]

    operations = [
        migrations.AlterField(
            model_name='devicesetting',
            name='mute_duration',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='devicesetting',
            name='sleep_duration',
            field=models.IntegerField(default=0),
        ),
    ]