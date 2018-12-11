import datetime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from wirfi_app.models import Device, DeviceSetting
from wirfi_app.serializers import DeviceMuteSettingSerializer, DevicePrioritySettingSerializer, DeviceSleepSerializer
from wirfi_app.views.caching import update_cached_device_list
from wirfi_app.views.create_admin_activity_log import create_activity_log


@api_view(['POST'])
def mute_device_view(request, id):
    try:
        device_obj = Device.objects.get(pk=id)
        device_setting, _ = DeviceSetting.objects.get_or_create(device=device_obj)
        mute_serializer = DeviceMuteSettingSerializer(device_setting, data=request.data)
        mute_serializer.is_valid(raise_exception=True)
        mute_serializer.save()

        create_activity_log(
            request,
            "Mute setting of device '{device}' of user '{email} updated.".format(device=device_obj.serial_number,
                                                                                 email=request.auth.user.email)
        )

        data_to_cache = {'id': device_setting.id,
                         'mute_start': (datetime.datetime.strptime(mute_serializer.data['mute_settings']['mute_start'],
                                                                   "%Y-%m-%dT%H:%M:%S.%fZ")).strftime(
                             '%Y-%m-%d %H:%M:%S.%f'),
                         'is_muted': mute_serializer.data['mute_settings']['is_muted'],
                         'mute_duration': mute_serializer.data['mute_settings']['mute_duration']}
        update_cached_device_list(data_to_cache)

        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Device Mute status is Changed.",
            'data': mute_serializer.data
        }

        return Response(data, status=status.HTTP_200_OK)

    except (AttributeError, ObjectDoesNotExist) as err:
        return Response({
            "code": getattr(settings, 'ERROR_CODE', 0),
            "message": str(err)},
            status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def device_priority_view(request, id):
    try:
        device = Device.objects.get(pk=id)
        device_setting, _ = DeviceSetting.objects.get_or_create(device=device)
        serializer = DevicePrioritySettingSerializer(device_setting, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        create_activity_log(
            request,
            "Priority of device '{device}' of user '{user}' updated.".format(device=device.serial_number,
                                                                             user=request.auth.user.email)
        )

        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Successfully priority updated.",
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)
    except (AttributeError, ObjectDoesNotExist) as err:
        return Response({
            "code": getattr(settings, 'ERROR_CODE', 0),
            "message": str(err)},
            status=status.HTTP_400_BAD_REQUEST)


class DeviceSleepView(generics.CreateAPIView):
    serializer_class = DeviceSleepSerializer

    def get_queryset(self):
        device_obj = Device.objects.get(pk=self.kwargs['id'])
        device_setting, _ = DeviceSetting.objects.get_or_create(device=device_obj)
        return device_setting

    def create(self, request, *args, **kwargs):
        instance = self.get_queryset()
        serializer = DeviceSleepSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data_to_cache = {'id': instance.id,
                         'sleep_start': (datetime.datetime.strptime(serializer.data['sleep_settings']['sleep_start'],
                                                                    "%Y-%m-%dT%H:%M:%S.%fZ")).strftime(
                             '%Y-%m-%d %H:%M:%S.%f'),
                         'is_asleep': serializer.data['sleep_settings']['is_asleep'],
                         'sleep_duration': serializer.data['sleep_settings']['sleep_duration']}

        update_cached_device_list(data_to_cache)

        create_activity_log(
            request,
            "Sleep setting of device '{device}' of user '{email} updated.".format(device=instance.device.serial_number,
                                                                                 email=request.auth.user.email)
        )

        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Successfully sleep settings updated.",
            'data': serializer.data
        }

        return Response(data, status=status.HTTP_200_OK)
