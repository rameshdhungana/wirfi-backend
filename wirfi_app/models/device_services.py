from django.db import models

from wirfi_app.models.device import Device

URGENT_UNREAD = 1
UNREAD = 2
READ = 3

NOTIFICATION_TYPE = (
    (URGENT_UNREAD, 'Urgent Unread'),
    (UNREAD, 'Unread'),
    (READ, 'Read')
)


class DeviceCameraServices(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="camera_service")
    is_on = models.BooleanField(default=False)
    serial_no = models.CharField(max_length=50)


class DeviceNotification(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='device_notification')
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.IntegerField(choices=NOTIFICATION_TYPE, default=2)
    message = models.CharField(max_length=255)
    description = models.TextField(blank=True)
