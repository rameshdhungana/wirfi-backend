# Generated by Django 2.0.7 on 2018-09-13 10:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wirfi_app', '0030_merge_20180911_0948'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeviceCameraServices',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_on', models.BooleanField(default=False)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wirfi_app.Device')),
            ],
        ),
        migrations.AddField(
            model_name='devicesetting',
            name='has_sleep_feature',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='devicesetting',
            name='is_asleep',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='devicesetting',
            name='sleep_duration',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='devicesetting',
            name='sleep_start',
            field=models.DateTimeField(auto_now=True),
        ),
    ]