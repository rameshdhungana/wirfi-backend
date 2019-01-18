from django.db import models
from wirfi_app.models.device import Device

DEVICE_STATUS = (
    (6, 'ONLINE'),
    (5, 'CELL'),
    (4, 'WEAK SIGNAL'),
    (3, 'MISSED A PING'),
    (2, 'OFFLINE'),
    (1, 'ASLEEP')
)

STATUS_COLOR = (
    (6, '#4aec26'),
    (5, '#5576e4'),
    (4, '#f0fc00'),
    (3, '#faac00'),
    (2, '#dd0000'),
    (1, '#808080')
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
    status = models.IntegerField(choices=DEVICE_STATUS, default=2)
    timestamp = models.DateTimeField(auto_now_add=True)
