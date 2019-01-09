import pusher
from django.conf import settings
from django.db.models import Q

from rest_framework import status, generics
from rest_framework.response import Response

from wirfi_app.models import Device, DEVICE_STATUS, DeviceStatus, DeviceNotification
from wirfi_app.models.device_services import URGENT_UNREAD, UNREAD
from wirfi_app.serializers import DeviceSerializer, DeviceStatusSerializer, DeviceNotificationSerializer

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
    An API to create and list device status.
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
        device_status = DeviceStatus.objects.create(device=device, status=request.data['status'])

        priority_device = device.device_settings.priority

        data = STATUS_DESCRIPTION[device_status.status]
        data['type'] = URGENT_UNREAD if priority_device else UNREAD
        data['device_status'] = str(device_status.status)

        serializer = DeviceNotificationSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(device=device)
        if priority_device:
            notification_count = DeviceNotification.objects.\
                                        filter(device__user=request.user).\
                                        filter(Q(type=URGENT_UNREAD) | Q(type=UNREAD)).count()
            pusher_notification(email=request.auth.user.email, message=serializer.data, count=notification_count)

        return Response({
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': 'Device status successfully added.'
        }, status=status.HTTP_201_CREATED)


def pusher_notification(email, message, count):
    pusher_client = pusher.Pusher(
        app_id=settings.PUSHER_APP_ID,
        key=settings.PUSHER_KEY,
        secret=settings.PUSHER_SECRET,
        cluster=settings.PUSHER_CLUSTER,
        ssl=True
    )
    pusher_client.trigger(email, 'status-change', {'message': message, 'count': count})
