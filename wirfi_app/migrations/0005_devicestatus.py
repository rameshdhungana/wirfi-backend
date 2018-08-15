# Generated by Django 2.0.7 on 2018-08-15 07:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wirfi_app', '0004_profile_address'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeviceStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(1, 'ONLINE'), (2, 'USING CELLULAR'), (3, 'WITH POOR SIGNAL'), (4, 'MISSED PING'), (5, 'OFFLINE'), (6, 'ASLEEP')], default=6)),
                ('device', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='wirfi_app.Device')),
            ],
        ),
    ]
