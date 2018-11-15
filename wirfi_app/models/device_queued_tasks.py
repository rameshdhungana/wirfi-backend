from django.db import models
from django.contrib.postgres.fields import JSONField


class QueueTaskForWiRFiDevice(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    data = JSONField()
    queued_status = models.BooleanField(default=True)
