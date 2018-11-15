import urllib
from urllib.parse import urlparse
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from wirfi_app.models import DeviceNetwork, QueueTaskForWiRFiDevice

DEVICE_NETWORK = 'DeviceNetwork'
QUEUE_TASK_MODEL = (DEVICE_NETWORK, 'DeviceNetwork')


@receiver(post_save, sender=DeviceNetwork)
def queue_task_for_wirfi_device(sender, instance, **kwargs):
    print('sender:', sender, 'instance:', instance, instance.__class__.__name__)
    queue_obj = QueueTaskForWiRFiDevice.objects.create(data={'model': instance.__class__.__name__,
                                                             'ssid_name': instance.ssid_name,
                                                             'password': instance.password,
                                                             'device_serial_number': instance.device.serial_number,
                                                             'device_id': instance.device.id

                                                             })

    if instance.primary_network:
        queue_obj.data['action'] = 'Primary Network Changed'

    else:
        queue_obj.data['action'] = 'Secondary Network Changed'

    queue_obj.save()
    print(queue_obj.__dict__)


@api_view(['POST'])
def ping_server_from_wirfi_device(request):
    print('this is checking wirfi_device')
    # request.body gets the post data passed from the device while pinging this view
    #  request.body is byte stream hence decode it to utf-8 format and parse it to dict form
    parsed_data = urllib.parse.parse_qs(request.body.decode('utf-8'))
    # this parsing gives value in list format with dict, hence we use [0]
    device_serial_number = parsed_data['device_serial_number'][0]
    print(device_serial_number)
    print(type(device_serial_number))
    print(parsed_data)

    queue_tasks = QueueTaskForWiRFiDevice.objects.filter(queued_status=True,
                                                         data__device_serial_number=device_serial_number)
    response_data = {}
    for key, task in enumerate(queue_tasks):
        print(key, task)
        if task.data['model'] == DEVICE_NETWORK:
            response_data = {'model': task.data['model'],
                             'data': {'ssid_name': task.data['ssid_name'],
                                      'password': task.data['password']
                                      }
                             }
        task.queued_status = False
        task.save()
        print(response_data)

    return Response(response_data, status=status.HTTP_200_OK)
