from django.db import models
from django.contrib.postgres.fields import JSONField

from wirfi_app.models import Device

PRIMARY_NETWORK_CHANGED = 'primary_network_changed'
SECONDARY_NETWORK_CHANGED = 'secondary_network_changed'
DEVICE_CREATED = 'device_created'
NO_TASK = 'no task'

ACTIONS = (
    (PRIMARY_NETWORK_CHANGED, 'primary_network_changed'),
    (SECONDARY_NETWORK_CHANGED, 'secondary_network_changed'),
    (DEVICE_CREATED, 'device_created'),
    (NO_TASK, 'no task')
)


class QueueTaskForWiRFiDevice(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    data = JSONField()
    queued_status = models.BooleanField(default=True)
    action = models.CharField(choices=ACTIONS, default=NO_TASK, max_length=64)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='queue_tasks')

    class Meta:
        ordering = ('created_at',)
        unique_together = ('action', 'device')
