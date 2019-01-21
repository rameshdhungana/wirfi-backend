from django.conf import settings
from django.db.models import Q

from rest_framework import status, generics
from rest_framework.response import Response

from wirfi_app.models import Device, DEVICE_STATUS, DeviceStatus, DeviceNotification
from wirfi_app.models.device_services import URGENT_UNREAD, UNREAD
from wirfi_app.serializers import DeviceSerializer, DeviceStatusSerializer, DeviceNotificationSerializer
from wirfi_app.views.pusher_notification import pusher_notification

STATUS_DESCRIPTION = {
    '6': {'message': 'Went back online'},
    '5': {'message': 'Cell'},
    '4': {'message': 'Poor connection'},
    '3': {'message': 'Missed a ping'},
    '2': {'message': 'Lost connection to the internet'},
    '1': {'message': 'Asleep'},
}


class DeviceStatusView(generics.ListCreateAPIView):
    '''
    An API to update device status.
    '''
    serializer_class = DeviceStatusSerializer

    def get_queryset(self):
        return Device.objects.filter(user=self.request.auth.user)

    def list(self, request, *args, **kwargs):
        devices = DeviceSerializer(self.get_queryset(), many=True).data
        return Response({
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': 'Device and status successfully fetched.',
            'data': {
                'status': [{'id': key, 'name': value} for key, value in DEVICE_STATUS],
                'devices': devices
            }
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        device = Device.objects.get(pk=request.data['device'])
        prev_device_status = DeviceStatus.objects.filter(device=device).last()
        device_status = DeviceStatus.objects.create(device=device, status=int(request.data['status']))

        same_status = device_status.status == prev_device_status.status if prev_device_status else False

        if not same_status:
            priority_device = device.device_settings.priority
            urgent_unread = device_status.status in [2, 3]

            data = STATUS_DESCRIPTION[str(device_status.status)]
            data['type'] = URGENT_UNREAD if urgent_unread else UNREAD
            data['device_status'] = str(device_status.status)

            serializer = DeviceNotificationSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save(device=device)

            # pusher trigger
            if priority_device or urgent_unread:
                notification_count = DeviceNotification.objects.\
                                            filter(device__user=request.user).\
                                            filter(Q(type=URGENT_UNREAD) | Q(type=UNREAD)).count()

                event_name = 'priority-device' if priority_device else 'status-change'
                pusher_notification(channel=str(request.auth.user.id), event=event_name,
                                    data={'message': serializer.data, 'count': notification_count})

        return Response({
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': 'Device status successfully updated.'
        }, status=status.HTTP_201_CREATED)
