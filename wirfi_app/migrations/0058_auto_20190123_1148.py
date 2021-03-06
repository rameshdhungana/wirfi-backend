# Generated by Django 2.0.7 on 2019-01-23 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wirfi_app', '0057_devicepingstatus'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='devicestatus',
            options={'ordering': ('-pk',)},
        ),
        migrations.AddField(
            model_name='devicepingstatus',
            name='device_ip_address',
            field=models.GenericIPAddressField(null=True),
        ),
        migrations.AddField(
            model_name='devicepingstatus',
            name='network_strength',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='devicepingstatus',
            name='pinged_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
