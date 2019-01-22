from django.db import models
from wirfi_app.models import Device


class DevicePingStatus(models.Model):
    pinged_at = models.DateTimeField(auto_now=True)
    device = models.OneToOneField(Device, on_delete=models.CASCADE, related_name='ping_status')
