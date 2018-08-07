# Generated by Django 2.0.7 on 2018-08-06 10:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wirfi_app', '0002_auto_20180806_0907'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuthorizationToken',
            fields=[
                ('key', models.CharField(max_length=40, primary_key=True, serialize=False, verbose_name='Key')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('device_id', models.CharField(blank=True, max_length=128)),
                ('push_notification_token', models.CharField(blank=True, max_length=128, unique=True)),
                ('device_type', models.IntegerField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Token',
                'verbose_name_plural': 'Tokens',
            },
        ),
        migrations.RemoveField(
            model_name='authenticationinfo',
            name='datetimemodel_ptr',
        ),
        migrations.DeleteModel(
            name='AuthenticationInfo',
        ),
    ]