# Generated by Django 2.0.7 on 2018-08-07 11:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('wirfi_app', '0005_auto_20180807_0600'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='latitude',
            field=models.DecimalField(decimal_places=12, default=0, max_digits=15),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='device',
            name='longitude',
            field=models.DecimalField(decimal_places=12, default=0, max_digits=15),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='authorizationtoken',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='auth_token', to=settings.AUTH_USER_MODEL),
        ),
    ]