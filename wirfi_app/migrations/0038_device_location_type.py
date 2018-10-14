# Generated by Django 2.0.7 on 2018-10-05 11:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wirfi_app', '0037_auto_20181004_0614'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='location_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='location_type', to='wirfi_app.Franchise'),
            preserve_default=False,
        ),
    ]
