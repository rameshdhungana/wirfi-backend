import urllib
from urllib.parse import urlparse
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

from wirfi_app.models import DeviceNetwork, QueueTaskForWiRFiDevice, Device

DEVICE_NETWORK = 'DeviceNetwork'
DEVICE = 'Device'
PRIMARY_NETWORK_CHANGED = 'primary_network_changed'
SECONDARY_NETWORK_CHANGED = 'secondary_network_changed'
DEVICE_CREATED = 'device_created'


def device_created(task, **data_to_store):
    print(data_to_store, 'this is data to store', task.data['device_serial_number'])
    try:
        device_obj = Device.objects.get(serial_number=task.data['device_serial_number'])
        print(device_obj)
        # we try to get the devicenetwork instance with device id from obtained from queue task object
        # if we obtain we update it (this rarely happens , is case of exception)
        # else we create device network object with the credentials obtained from device
        try:
            device_network_obj = DeviceNetwork.objects.get(device=device_obj, primary_network=True)
            device_network_obj.ssid_name = data_to_store['primary_ssid_name']
            device_network_obj.password = data_to_store['primary_password']
            device_network_obj.primary_network = True
            device_network_obj.save()
        except:
            DeviceNetwork.objects.create(
                device=device_obj, ssid_name=data_to_store['primary_ssid_name'],
                password=data_to_store['primary_password'],
                primary_network=True)

        response_data = {'code': getattr(settings, 'SUCCESS_CODE', 1),
                         'action': task.action,
                         'device_serial_number': task.data['device_serial_number'],

                         }
        task.queued_status = False
        task.save()
    except:
        print('except data')
        response_data = {'code': getattr(settings, 'ERROR_CODE', 0),
                         'action': task.action,
                         'device_serial_number': task.data['device_serial_number'],

                         }

    return response_data


def device_network_setting_changed(task, **kwargs):
    print('this is network task', kwargs)

    response_data = {
        'code': getattr(settings, 'SUCCESS_CODE', 1),
        'action': task.action,
        'device_serial_number': task.data['device_serial_number'],
        'data': {'ssid_name': task.data['ssid_name'],
                 'password': task.data['password']
                 }
    }
    task.queued_status = False
    task.save()
    return response_data


tasks_map = {
    DEVICE_CREATED: device_created,
    PRIMARY_NETWORK_CHANGED: device_network_setting_changed,
    SECONDARY_NETWORK_CHANGED: device_network_setting_changed
}


@api_view(['POST'])
def ping_server_from_wirfi_device(request):
    print('this is checking wirfi_device')
    # request.body gets the post data passed from the device while pinging this view
    #  request.body is byte stream hence decode it to utf-8 format and parse it to dict form
    parsed_data = urllib.parse.parse_qs(request.body.decode('utf-8'))
    print(parsed_data)
    # this parsing gives value in list format with dict, hence we use [0]
    response_data = []

    try:

        device_serial_number = parsed_data['device_serial_number'][0]

        # this dictionary's key value pair  will depend upon which function to call depending upon if conditions
        data_to_store = {}
        if 'primary_ssid_name' in parsed_data and 'primary_password':
            data_to_store['primary_ssid_name'] = parsed_data['primary_ssid_name'][0]
            data_to_store['primary_password'] = parsed_data['primary_password'][0]

        queued_tasks = QueueTaskForWiRFiDevice.objects.filter(queued_status=True,
                                                              device__serial_number=device_serial_number)

        for key, task in enumerate(queued_tasks):
            print(task)
            if task.queued_status:
                response = tasks_map[task.action](task, **data_to_store)
                response_data.append(response)

            print(response_data, 'this is response from queue function')

        return Response(response_data, status=status.HTTP_200_OK)
    except:
        response = {
            'message': 'something went wrong',
            'code': getattr(settings, 'ERROR_CODE', 0),

        }
        response_data.append(response)
        return Response(response_data)
