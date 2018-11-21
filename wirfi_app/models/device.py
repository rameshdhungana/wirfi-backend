from django.db import models
from django.conf import settings

from wirfi_app.models.industry_franchise_type import Industry, Franchise

User = settings.AUTH_USER_MODEL


class Device(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    serial_number = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=30)
    location_logo = models.ImageField(upload_to='device/images', null=True)
    machine_photo = models.ImageField(upload_to='device/images', null=True)
    location_of_device = models.CharField(max_length=128, verbose_name="location_of_device")
    address = models.CharField(max_length=100, verbose_name="device_address")
    latitude = models.FloatField(default=0)
    longitude = models.FloatField(default=0)
    industry_type = models.ForeignKey(Industry, on_delete=models.CASCADE, related_name="industry_type")
    location_type = models.ForeignKey(Franchise, on_delete=models.CASCADE, related_name="location_type")
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.serial_number
