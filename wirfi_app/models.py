from __future__ import unicode_literals

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
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=15, decimal_places=12)
    longitude = models.DecimalField(max_digits=15, decimal_places=12)
    email = models.EmailField()
    strip_token = models.TextField()

    def __str__(self):
        return self.card_number


class Device(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    serial_number = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=30)
    location_logo = models.ImageField(upload_to='device/images')
    location_photo = models.ImageField(upload_to='device/images')
    # location_hours = models.DecimalField(max_digits=10, decimal_places=1, null=True)
    ssid_name = models.CharField(max_length=50)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.serial_number


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


class AuthenticationInfo(DateTimeModel):
    device_id = models.CharField(max_length=128, blank=True)
    auth_key = models.CharField(max_length=128)
    refresh_token = models.CharField(max_length=128)
    push_notification_token = models.CharField(max_length=128, blank=True)
    device_type = models.IntegerField(null=True, blank=True)
