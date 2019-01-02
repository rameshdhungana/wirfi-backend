from django.db import models
from wirfi_app.models.device import Device

DEVICE_STATUS = (
    (6, 'ONLINE'),
    (5, 'CELL'),
    (4, 'WEAK SIGNAL'),
    (3, 'MISSED A PING'),
    (2, 'OFFLINE'),
    (1, 'ASLEEP'),
)


class DeviceLocationHours(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="location_hours")
    day_id = models.PositiveSmallIntegerField()
    from_time = models.TimeField()
    to_time = models.TimeField()
    is_on = models.BooleanField(default=True)


class DeviceNetwork(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="device_network")
    ssid_name = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    primary_network = models.BooleanField()


class DeviceStatus(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="status")
    status = models.IntegerField(choices=DEVICE_STATUS, default=1)
    timestamp = models.DateTimeField(auto_now_add=True)
