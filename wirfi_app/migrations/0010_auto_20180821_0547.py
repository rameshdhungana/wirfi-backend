# Generated by Django 2.0.7 on 2018-08-21 05:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wirfi_app', '0009_merge_20180817_0828'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='address',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='profile',
            name='address',
            field=models.CharField(max_length=100),
        ),
    ]
