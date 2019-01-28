from django.db import models

from wirfi_app.models.device import Device


class DeviceSetting(models.Model):
    device = models.OneToOneField(Device, on_delete=models.CASCADE, related_name='device_settings')
    is_muted = models.BooleanField(default=False)
    mute_start = models.DateTimeField(auto_now=True)
    mute_duration = models.IntegerField(default=0)
    priority = models.BooleanField(default=False)
    has_sleep_feature = models.BooleanField(default=True)
    is_asleep = models.BooleanField(default=False)
    sleep_start = models.DateTimeField(auto_now=True)
    sleep_duration = models.IntegerField(default=0)
