from __future__ import unicode_literals

import binascii
import os

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import gettext_lazy as _

from .managers import UserManager

PLAN_INTERVAL = 'month'
PLAN_CURRENCY = 'usd'

DEVICE_STATUS = (
    (6, 'ONLINE'),
    (5, 'CELL'),
    (4, 'AUTO RECOVER'),
    (3, 'WEAK SIGNAL'),
    (2, 'OFFLINE'),
    (1, 'ASLEEP'),
)
URGENT_UNREAD = 1
UNREAD = 2
READ = 3

NOTIFICATION_TYPE = (
    (URGENT_UNREAD, 'Urgent Unread'),
    (UNREAD, 'Unread'),
    (READ, 'Read')
)


class DateTimeModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


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

    @property
    def full_name(self):
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


class Industry(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)


class Franchise(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = ('name', 'user')


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_picture = models.ImageField(upload_to='users/profile_pictures', null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.full_name


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
    customer_id = models.CharField(max_length=64)

    def __str__(self):
        return self.user.email


class Device(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    serial_number = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=30)
    location_logo = models.ImageField(upload_to='device/images', null=True)
    machine_photo = models.ImageField(upload_to='device/images', null=True)
    address = models.CharField(max_length=100)
    latitude = models.FloatField(default=0)
    longitude = models.FloatField(default=0)
    industry_type = models.ForeignKey(Industry, on_delete=models.CASCADE, related_name="industry_type")
    location_type = models.ForeignKey(Franchise, on_delete=models.CASCADE, related_name="location_type")
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.serial_number


class DeviceNetwork(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="device_network")
    ssid_name = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    primary_network = models.BooleanField()


class DeviceLocationHours(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="location_hours")
    day_id = models.PositiveSmallIntegerField()
    from_time = models.TimeField()
    to_time = models.TimeField()
    is_on = models.BooleanField(default=True)


class DeviceStatus(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="status")
    status = models.IntegerField(choices=DEVICE_STATUS, default=6)
    timestamp = models.DateTimeField(auto_now_add=True)


class DeviceNotification(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='device_notification')
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.IntegerField(choices=NOTIFICATION_TYPE, default=2)
    message = models.CharField(max_length=255)
    description = models.TextField(blank=True)


class DeviceSetting(models.Model):
    device = models.OneToOneField(Device, on_delete=models.CASCADE, related_name='device_settings')
    is_muted = models.BooleanField(default=False)
    mute_start = models.DateTimeField(auto_now=True)
    mute_duration = models.IntegerField(default=0)
    priority = models.BooleanField(default=False)
    has_sleep_feature = models.BooleanField(default=False)
    is_asleep = models.BooleanField(default=False)
    sleep_start = models.DateTimeField(auto_now=True)
    sleep_duration = models.IntegerField(default=0)


class DeviceCameraServices(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="camera_service")
    is_on = models.BooleanField(default=False)
    serial_no = models.CharField(max_length=50)


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


class UserActivationCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="activation_code")
    code = models.CharField(max_length=12, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    count = models.PositiveIntegerField(default=1)
    once_used = models.BooleanField(default=False)


class PresetFilter(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    filter_type = models.PositiveIntegerField()
    filter_keys = ArrayField(models.IntegerField(null=True, blank=True))
    sort_type = models.PositiveIntegerField()

    class Meta:
        unique_together = ("user", "name")
