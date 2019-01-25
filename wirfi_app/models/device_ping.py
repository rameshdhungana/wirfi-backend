from django.db import models
from wirfi_app.models import Device


class DevicePingStatus(models.Model):
    pinged_at = models.DateTimeField(auto_now_add=True)
    network_strength = models.FloatField(null=True)
    device_ip_address = models.GenericIPAddressField(null=True)
    device = models.OneToOneField(Device, on_delete=models.CASCADE, related_name='ping_status')
