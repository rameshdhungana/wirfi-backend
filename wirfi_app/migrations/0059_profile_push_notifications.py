# Generated by Django 2.0.7 on 2019-01-25 07:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wirfi_app', '0058_auto_20190123_1148'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='push_notifications',
            field=models.BooleanField(default=True),
        ),
    ]
