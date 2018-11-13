import binascii
import os

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.conf import settings

User = settings.AUTH_USER_MODEL


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