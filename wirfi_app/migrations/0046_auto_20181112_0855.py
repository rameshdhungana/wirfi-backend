# Generated by Django 2.0.7 on 2018-11-12 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wirfi_app', '0045_queuetaskforwirfidevice'),
    ]

    operations = [
        migrations.AlterField(
            model_name='queuetaskforwirfidevice',
            name='queued_status',
            field=models.BooleanField(default=True),
        ),
    ]
