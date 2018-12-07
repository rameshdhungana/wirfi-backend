from django.conf import settings

from rest_framework import generics, status
from rest_framework.response import Response

from wirfi_app.models import Device, DeviceCameraServices
from wirfi_app.serializers import DeviceCameraSerializer
from wirfi_app.views.create_admin_activity_log import create_activity_log


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
        user = request.auth.user
        device_obj = Device.objects.get(pk=self.kwargs['id'])
        serializer = DeviceCameraSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(device=device_obj)

        create_activity_log(
            request,
            "Camera information for device '{s_no}' of user '{email}' added.".format(s_no=device_obj.serial_number,
                                                                                     email=user.email)
        )

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
        camera = self.get_object()
        serializer = DeviceCameraSerializer(camera, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        create_activity_log(
            request,
            "Camera information for device '{s_no}' of user '{email}' updated.".format(
                s_no=camera.camera_service.serial_number,
                email=request.auth.user.email
            )
        )
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Sucesfully updated device's camera information.",
            'data': {'camera_service': serializer.data}
        }
        return Response(data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        camera = self.get_object()
        create_activity_log(
            request,
            "Camera information for device '{s_no}' of user '{email}' deleted.".format(
                s_no=camera.camera_service.serial_number,
                email=request.auth.user.email
            )
        )
        camera.delete()
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Sucesfully deleted device's camera information."
        }
        return Response(data, status=status.HTTP_200_OK)
