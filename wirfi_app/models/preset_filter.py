from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField

User = settings.AUTH_USER_MODEL


class PresetFilter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    filter_type = models.PositiveIntegerField()
    filter_keys = ArrayField(models.IntegerField(null=True, blank=True))
    sort_type = models.PositiveIntegerField()

    class Meta:
        unique_together = ("user", "name")