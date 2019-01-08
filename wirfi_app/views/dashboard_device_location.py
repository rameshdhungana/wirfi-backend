from rest_framework import generics

from wirfi_app.models import Device
from wirfi_app.serializers import DeviceLocationSerializer


class DeviceLocation(generics.ListAPIView):
    '''
    API to list logged in user's all devices' location.
    '''
    serializer_class = DeviceLocationSerializer

    def get_queryset(self):
        return Device.objects.filter(user=self.request.user)
