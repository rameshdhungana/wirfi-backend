from django.db import models
from django.contrib.auth.models import AbstractUser


class DateTimeModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract: True


class User(AbstractUser, DateTimeModel):
    pass


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='users/profile_pictures', null=True, blank=True)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name


class BusinessInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class BillingInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    card_number = models.IntegerField()
    security_code = models.IntegerField()
    expiration_date = models.DateField()

    def __str__(self):
        return self.card_number


class Device(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    serial_number = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=30)
    location_logo = models.ImageField(upload_to='device/images')
    location_photo = models.ImageField(upload_to='device/images')
    location_hours = models.DecimalField(max_digits=10, decimal_places=1)

    def __str__(self):
        return self.serial_number


class DeviceNetwork(models.Model):
    device = models.OneToOneField(Device, on_delete=models.CASCADE)
    ssid_name = models.CharField(max_length=50)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.device.serial_number
