import urllib
from datetime import datetime
from urllib.parse import urlparse

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from pytz import utc
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from wirfi_app.models import DeviceNetwork, QueueTaskForWiRFiDevice, Device, DevicePingStatus

PRIMARY_NETWORK_CHANGED = 'primary_network_changed'
DEVICE_CREATED = 'device_created'
DEVICE_REBOOT = 'device_reboot'


def device_reboot(task, **data_to_store):
    response_data = {
        'code': getattr(settings, 'SUCCESS_CODE', 1),
        'action': task.action,
        'device_serial_number': task.data['device_serial_number'],
    }
    return response_data


def device_created(task, **data_to_store):
    print(data_to_store, 'this is data to store', task.data['device_serial_number'])
    try:
        device_obj = Device.objects.get(serial_number=task.data['device_serial_number'])
        print(device_obj)
        # we try to get the devicenetwork instance with device id from obtained from queue task object,
        # if we obtain, we update it (this rarely happens , is case of exception)
        # else we create device network object with the credentials obtained from device
        try:
            device_network_obj = DeviceNetwork.objects.get(device=device_obj, primary_network=True)
            device_network_obj.ssid_name = data_to_store['primary_ssid_name']
            device_network_obj.password = data_to_store['primary_password']
            device_network_obj.primary_network = True
            device_network_obj.save()
        except ObjectDoesNotExist:
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
    print('this is network task')

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
    PRIMARY_NETWORK_CHANGED: device_network_setting_changed,
    DEVICE_REBOOT: device_reboot

}


def update_device_ping_status_table(request, device_serial_number, network_strength):
    device_obj = Device.objects.get(serial_number=device_serial_number)
    # each time device pings the server, its pinged_at value is updated to current datetime field
    device_ping_status_obj, created = DevicePingStatus.objects.get_or_create(device=device_obj)
    print(device_ping_status_obj, 'this is device ping status object', device_ping_status_obj.pinged_at)
    device_ping_status_obj.pinged_at = datetime.now().replace(tzinfo=utc)
    device_ping_status_obj.device_ip_address = get_client_ip(request)
    device_ping_status_obj.network_strength = network_strength
    device_ping_status_obj.save()


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class DeviceIsAuthenticated(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        parsed_data = urllib.parse.parse_qs(request.body.decode('utf-8'))
        print(parsed_data)
        # this parsing gives value in list format with dict, hence we use [0]
        # checks if the device_secret_key obtained from device matches our setting specified secret key
        return getattr(settings, 'SECRET_KEY_FOR_DEVICE_TO_ACCESS_SERVER', 'qRY,1QC;>#^,S|6M*Ky~<m-+p{ADEfWIRFI') == \
               parsed_data['secret_key_to_access_server'][0]


@api_view(['POST'])
@permission_classes((DeviceIsAuthenticated,))
def ping_server_from_wirfi_device(request):
    # request.body gets the post data passed from the device while pinging this view
    #  request.body is byte stream hence decode it to utf-8 format and parse it to dict form
    parsed_data = urllib.parse.parse_qs(request.body.decode('utf-8'))
    print(parsed_data)
    # this parsing gives value in list format with dict, hence we use [0]
    response_data = []

    try:

        device_serial_number = parsed_data['device_serial_number'][0]
        network_strength = parsed_data['network_strength'][0]
        update_device_ping_status_table(request, device_serial_number, network_strength)
        print('this is checking wirfi_device')
        print(get_client_ip(request))

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
        print('inside except')
        response = {
            'message': 'something went wrong',
            'code': getattr(settings, 'ERROR_CODE', 0),

        }
        response_data.append(response)
        return Response(response_data)


@api_view(['POST'])
@permission_classes((DeviceIsAuthenticated,))
def set_device_primary_network_settings(request):
    # request.body gets the post data passed from the device while pinging this view
    #  request.body is byte stream hence decode it to utf-8 format and parse it to dict form
    parsed_data = urllib.parse.parse_qs(request.body.decode('utf-8'))
    print(parsed_data)
    # this parsing gives value in list format with dict, hence we use [0]

    # this dictionary's key value pair  will depend upon which function to call depending upon if conditions
    data_to_store = {}
    if 'primary_ssid_name' in parsed_data and 'primary_password' in parsed_data:

        try:
            device_serial_number = parsed_data['device_serial_number'][0]
            device_network_obj, created = DeviceNetwork.objects.get_or_create(
                device__serial_number=device_serial_number, primary_network=True)
            device_network_obj.ssid_name = parsed_data['primary_ssid_name'][0]
            device_network_obj.password = parsed_data['primary_password'][0]
            device_network_obj.primary_network = True
            device_network_obj.save()

            response_data = {'code': getattr(settings, 'SUCCESS_CODE', 1),
                             'device_serial_number': parsed_data['device_serial_number'][0]

                             }
            return Response(response_data)

        except ObjectDoesNotExist:
            print('except data')
            response_data = {'code': getattr(settings, 'ERROR_CODE', 0),
                             'device_serial_number': parsed_data['device_serial_number']

                             }
            return Response(response_data)
