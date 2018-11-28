from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class AdminActivityLog(models.Model):
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    activity = models.TextField()
