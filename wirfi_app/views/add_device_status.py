from django.conf import settings

from rest_framework import status, generics
from rest_framework.response import Response

from wirfi_app.models import Device, DEVICE_STATUS
from wirfi_app.serializers import DeviceSerializer, DeviceStatusSerializer


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
        serializer = DeviceStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': 'Device status successfully added.'
        }, status=status.HTTP_201_CREATED)
