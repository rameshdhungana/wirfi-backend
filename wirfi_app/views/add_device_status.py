import pusher
from django.conf import settings

from rest_framework import status, generics
from rest_framework.response import Response

from wirfi_app.models import Device, DEVICE_STATUS, DeviceStatus
from wirfi_app.models.device_services import URGENT_UNREAD, UNREAD
from wirfi_app.serializers import DeviceSerializer, DeviceStatusSerializer, DeviceNotificationSerializer

STATUS_DESCRIPTION = {
    '6': {'message': 'Went back online',
          'type': URGENT_UNREAD},
    '5': {'message': 'Cell',
          'type': UNREAD},
    '4': {'message': 'Auto recover',
          'type': UNREAD},
    '3': {'message': 'Poor connection',
          'type': UNREAD},
    '2': {'message': 'Lost connection to the internet',
          'type': URGENT_UNREAD},
    '1': {'message': 'Asleep',
          'type': UNREAD},
}


class DeviceStatusView(generics.ListCreateAPIView):
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

        data = STATUS_DESCRIPTION[device_status.status]
        serializer = DeviceNotificationSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(device=device)
        message = '{}: {}'.format(device.name, data['message'])
        pusher_notification(email=request.auth.user.email, message=message)

        return Response({
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': 'Device status successfully added.'
        }, status=status.HTTP_201_CREATED)


def pusher_notification(email, message):
    pusher_client = pusher.Pusher(
        app_id=settings.PUSHER_APP_ID,
        key=settings.PUSHER_KEY,
        secret=settings.PUSHER_SECRET,
        cluster=settings.PUSHER_CLUSTER,
        ssl=True
    )
    pusher_client.trigger(email, 'status_change', {'message': message})
