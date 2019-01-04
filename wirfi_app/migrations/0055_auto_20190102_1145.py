# Generated by Django 2.0.7 on 2019-01-02 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wirfi_app', '0054_auto_20190102_1144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='devicestatus',
            name='status',
            field=models.IntegerField(choices=[(6, 'ONLINE'), (5, 'CELL'), (4, 'WEAK SIGNAL'), (3, 'MISSED A PING'), (2, 'OFFLINE'), (1, 'ASLEEP')], default=1),
        ),
    ]
