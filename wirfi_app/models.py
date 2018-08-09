from __future__ import unicode_literals

import binascii
import os

from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import gettext_lazy as _

from .managers import UserManager

PLAN_INTERVAL = 'month'
PLAN_CURRENCY = 'usd'


class DateTimeModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract: True


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        '''
        Returns the short name for the user.
        '''
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def __str__(self):
        return self.email


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
    latitude = models.DecimalField(max_digits=15, decimal_places=12)
    longitude = models.DecimalField(max_digits=15, decimal_places=12)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class Billing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=15, decimal_places=12, null=True, blank=True)
    longitude = models.DecimalField(max_digits=15, decimal_places=12, null=True, blank=True)
    stripe_token = models.TextField()
    customer_id = models.CharField(max_length=64)

    def __str__(self):
        return self.user.email


class Device(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    serial_number = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=30)
    location_logo = models.ImageField(upload_to='device/images', null=True)
    machine_photo = models.ImageField(upload_to='device/images', null=True)
    latitude = models.DecimalField(max_digits=15, decimal_places=12, default=0)
    longitude = models.DecimalField(max_digits=15, decimal_places=12, default=0)

    def __str__(self):
        return self.serial_number


class DeviceNetwork(models.Model):
    device = models.OneToOneField(Device, on_delete=models.CASCADE, related_name="device_network")
    ssid_name = models.CharField(max_length=50)
    password = models.CharField(max_length=50)


class DeviceLocationHours(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="location_hours")
    day = models.CharField(max_length=9)
    from_time = models.TimeField()
    to_time = models.TimeField()
    is_on = models.BooleanField(default=True)
    whole_day = models.BooleanField(default=False)


class ServicePlan(DateTimeModel):
    stripe_id = models.CharField(max_length=255)
    name = models.CharField(max_length=128)
    interval = models.CharField(max_length=128, default=PLAN_INTERVAL)
    currency = models.CharField(max_length=128, default=PLAN_CURRENCY)
    amount = models.FloatField(null=True, blank=True)


class Subscription(DateTimeModel):
    customer_id = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    service_plan = models.ForeignKey(ServicePlan, on_delete=models.CASCADE)


class AuthorizationToken(models.Model):
    key = models.CharField(_("Key"), max_length=40, primary_key=True)
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auth_token")
    device_id = models.CharField(max_length=128, blank=True)
    push_notification_token = models.CharField(max_length=128, blank=True)
    device_type = models.IntegerField()

    class Meta:
        verbose_name = _("Token")
        verbose_name_plural = _("Tokens")

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key
