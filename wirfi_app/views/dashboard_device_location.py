from rest_framework import generics

from wirfi_app.models import Device
from wirfi_app.serializers import DeviceLocationSerializer


class DeviceLocation(generics.ListAPIView):
    serializer_class = DeviceLocationSerializer
    queryset = Device.objects.all()

    def get_queryset(self):
        print(self.request.user.id, self.queryset.filter(user=self.request.user).count(), self.queryset.count())

        return self.queryset.filter(user=self.request.user)
