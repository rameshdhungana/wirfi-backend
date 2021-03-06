# Generated by Django 2.0.7 on 2019-01-22 11:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wirfi_app', '0056_auto_20190103_0450'),
    ]

    operations = [
        migrations.CreateModel(
            name='DevicePingStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pinged_at', models.DateTimeField(auto_now=True)),
                ('device', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='ping_status', to='wirfi_app.Device')),
            ],
        ),
    ]
