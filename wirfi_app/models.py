from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.utils.translation import ugettext_lazy as _

from .managers import UserManager


<<<<<<< HEAD
class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()
=======
class DateTimeModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract: True


class User(AbstractUser, DateTimeModel):
    pass
>>>>>>> fa5be85673cd85b0ab5b7d4713d2e0bccb809d45


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='users/profile_pictures', null=True, blank=True)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name


class Business(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class Billing(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    card_number = models.BigIntegerField()
    security_code = models.BigIntegerField()
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
    ssid_name = models.CharField(max_length=50)
    password = models.CharField(max_length=100)

    def __str__(self):
<<<<<<< HEAD
        return self.serial_number
=======
        return self.device.serial_number
>>>>>>> fa5be85673cd85b0ab5b7d4713d2e0bccb809d45
