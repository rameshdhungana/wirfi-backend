# Generated by Django 2.0.7 on 2018-09-10 07:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wirfi_app', '0024_auto_20180910_0655'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useractivationcode',
            name='count',
            field=models.PositiveIntegerField(default=1),
        ),
    ]