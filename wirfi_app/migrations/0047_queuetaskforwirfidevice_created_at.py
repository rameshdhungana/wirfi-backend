# Generated by Django 2.0.7 on 2018-11-13 05:43

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('wirfi_app', '0046_auto_20181112_0855'),
    ]

    operations = [
        migrations.AddField(
            model_name='queuetaskforwirfidevice',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]