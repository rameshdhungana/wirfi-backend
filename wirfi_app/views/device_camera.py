from django.conf import settings

from rest_framework import generics, status
from rest_framework.response import Response

from wirfi_app.models import Device, DeviceCameraServices
from wirfi_app.serializers import DeviceCameraSerializer


class DeviceCameraView(generics.ListCreateAPIView):
    serializer_class = DeviceCameraSerializer

    def get_queryset(self):
        return DeviceCameraServices.objects.filter(device_id=self.kwargs['id'])

    def list(self, request, *args, **kwargs):
        serializer = DeviceCameraSerializer(self.get_queryset(), many=True)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Sucesfully fetched device's camera information.",
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        device_obj = Device.objects.get(pk=self.kwargs['id'])
        serializer = DeviceCameraSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(device=device_obj)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Sucesfully added device's camera information.",
            'data': {'camera_service': serializer.data}
        }
        return Response(data, status=status.HTTP_201_CREATED)


class DeviceCameraDetailView(generics.UpdateAPIView, generics.DestroyAPIView):
    serializer_class = DeviceCameraSerializer

    def get_queryset(self):
        return DeviceCameraServices.objects.filter(device_id=self.kwargs['device_id'])

    def update(self, request, *args, **kwargs):
        serializer = DeviceCameraSerializer(self.get_object(), data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Sucesfully updated device's camera information.",
            'data': {'camera_service': serializer.data}
        }
        return Response(data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Sucesfully deleted device's camera information."
        }
        return Response(data, status=status.HTTP_200_OK)