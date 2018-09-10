# Generated by Django 2.0.7 on 2018-09-10 11:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wirfi_app', '0025_auto_20180910_0715'),
    ]

    operations = [
        migrations.AddField(
            model_name='useractivationcode',
            name='once_used',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='useractivationcode',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='activation_code', to=settings.AUTH_USER_MODEL),
        ),
    ]
