# Generated by Django 2.0.7 on 2018-08-31 11:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wirfi_app', '0016_devicesetting'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeviceNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('type', models.IntegerField(choices=[(1, 'Urgent'), (2, 'Unread'), (3, 'Read')], default=2)),
                ('message', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='device_notification', to='wirfi_app.Device')),
            ],
        ),
        migrations.AlterField(
            model_name='devicestatus',
            name='status',
            field=models.IntegerField(choices=[(6, 'ONLINE'), (5, 'CELL'), (4, 'AUTO RECOVER'), (3, 'WEAK SIGNAL'), (2, 'OFFLINE'), (1, 'ASLEEP')], default=6),
        ),
    ]
