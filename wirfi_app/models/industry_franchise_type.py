from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Industry(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)


class Franchise(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = ('name', 'user')
