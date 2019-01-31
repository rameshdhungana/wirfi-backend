from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save
from django.dispatch import receiver

from wirfi_app.models import Device, QueueTaskForWiRFiDevice, DeviceNetwork

PRIMARY_NETWORK_CHANGED = 'primary_network_changed'
SECONDARY_NETWORK_CHANGED = 'secondary_network_changed'


@receiver(post_save, sender=DeviceNetwork)
def queue_device_network_task(sender, instance, created, **kwargs):
    print('sender:', sender, 'instance:', instance, instance.__class__.__name__)
    data_to_save = {'model': instance.__class__.__name__,
                    'ssid_name': instance.ssid_name,
                    'password': instance.password,
                    'device_serial_number': instance.device.serial_number,
                    'user_id': instance.device.id

                    }
    """ 
    first we search if the task object with given action for given device already exits, if it does we change its
    data field to values obtained from the post_save instance
    if the task object for given action to given device does not exit , we create it
    this will help us reduce number of duplications and also make filtering process faster
    """
    try:
        if instance.primary_network:
            queue_obj = QueueTaskForWiRFiDevice.objects.get(action=PRIMARY_NETWORK_CHANGED,
                                                            device=instance.device)
        else:
            queue_obj = QueueTaskForWiRFiDevice.objects.get(action=SECONDARY_NETWORK_CHANGED,
                                                            device=instance.device)
        queue_obj.data = data_to_save

    except ObjectDoesNotExist:

        queue_obj = QueueTaskForWiRFiDevice.objects.create(data={'model': instance.__class__.__name__,
                                                                 'ssid_name': instance.ssid_name,
                                                                 'password': instance.password,
                                                                 'device_serial_number': instance.device.serial_number,
                                                                 'device_id': instance.device.id,
                                                                 'user_id': instance.device.id

                                                                 }, device=instance.device)

        if instance.primary_network:
            queue_obj.action = PRIMARY_NETWORK_CHANGED
            queue_obj.data['description'] = 'Primary Network is changed'

        else:
            queue_obj.action = SECONDARY_NETWORK_CHANGED
            queue_obj.data['description'] = 'Secondary Network is changed'
    # set status boolean to True to indicate that it is task to be executed by device
    queue_obj.queued_status = True
    queue_obj.save()
    print(queue_obj.__dict__)
