from django.conf import settings

from rest_framework import generics, status
from rest_framework.response import Response

from wirfi_app.models import Device, DeviceCameraServices
from wirfi_app.serializers import DeviceCameraSerializer
from wirfi_app.views.create_admin_activity_log import create_activity_log
from django.http import StreamingHttpResponse
import redis
import base64

r = redis.Redis()

class DeviceCameraView(generics.ListCreateAPIView):
    '''
    API to create and list camera settings for device's id mentioned in the url
    '''
    serializer_class = DeviceCameraSerializer

    def get_queryset(self):
        return DeviceCameraServices.objects.filter(device_id=self.kwargs['id'])

    def list(self, request, *args, **kwargs):
        serializer = DeviceCameraSerializer(self.get_queryset(), many=True)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Successfully fetched device's camera information.",
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
            'message': "Successfully added device's camera information.",
            'data': {'camera_service': serializer.data}
        }
        return Response(data, status=status.HTTP_201_CREATED)


class DeviceCameraDetailView(generics.UpdateAPIView, generics.DestroyAPIView):
    '''
    API to update and delete camera setting of device's id mentioned in the url
    '''
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
            'message': "Successfully updated device's camera information.",
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
            'message': "Successfully deleted device's camera information."
        }
        return Response(data, status=status.HTTP_200_OK)


def get_frame(device_id):
    while True:
        frame_str = r.get(str(device_id))
        frame_byte = base64.b64decode(frame_str)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_byte + b'\r\n\r\n')

def stream(request, device_id):
    return StreamingHttpResponse(get_frame(device_id), content_type='multipart/x-mixed-replace; boundary=frame')