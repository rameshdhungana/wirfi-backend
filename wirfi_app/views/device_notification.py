from django.conf import settings

from rest_framework import generics, status
from rest_framework.response import Response

from wirfi_app.models import Device, DeviceNotification, NOTIFICATION_TYPE, READ
from wirfi_app.serializers import DeviceNotificationSerializer
from wirfi_app.views.login_logout import get_token_obj


class AllNotificationView(generics.ListAPIView):
    serializer_class = DeviceNotificationSerializer

    def get_each_type_queryset(self, type):
        return DeviceNotification.objects.filter(type=type).order_by('-id')

    def list(self, request, *args, **kwargs):
        notifications = []

        for index, (type_value, type_name) in enumerate(NOTIFICATION_TYPE):
            noti = self.get_each_type_queryset(type_value)
            serializer = DeviceNotificationSerializer(noti, many=True)

            notifications.append({"type": type_value, "type_name": type_name, "notifications": serializer.data})

        data = {
            "code": getattr(settings, 'SUCCESS_CODE', 1),
            'message': "All Notifications fetched successfully",
            "data":
                {"read_type": READ,
                 "notifications": notifications}
        }
        return Response(data, status=status.HTTP_200_OK)


class DeviceNotificationView(generics.CreateAPIView):
    serializer_class = DeviceNotificationSerializer

    def get_each_type_queryset(self, type):
        return DeviceNotification.objects.filter(device_id=self.kwargs['device_id'], type=type).order_by('-id')

    # def list(self, request, *args, **kwargs):
    #     notifications = []
    #
    #     for index, (type_value, type_name) in enumerate(NOTIFICATION_TYPE):
    #         noti = self.get_each_type_queryset(type_value)
    #         serializer = DeviceNotificationSerializer(noti, many=True)
    #
    #         notifications.append({"type": type_value, "type_name": type_name, "notifications": serializer.data})
    #
    #     data = {
    #         "code": getattr(settings, 'SUCCESS_CODE', 1),
    #         'message': "Notifications fetched successfully",
    #         "data":
    #             {"read_type": READ,
    #              "notifications": notifications}
    #     }
    #     return Response(data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        device = Device.objects.get(pk=self.kwargs['device_id'])
        serializer = DeviceNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(device=device)
        data = {
            "code": getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Device Notifications created successfully",
            "data": serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)


class UpdateNotificationView(generics.UpdateAPIView, generics.DestroyAPIView):
    serializer_class = DeviceNotificationSerializer
    queryset = DeviceNotification.objects.all()

    def update(self, request, *args, **kwargs):
        notification = self.get_object()
        notification.type = READ
        notification.save()
        data = {
            "code": getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Notifications is updated to READ Type successfully",
        }
        return Response(data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return Response({
            "code": getattr(settings, 'SUCCESS_CODE', 1),
            "message": "Successfully deleted notification."
        }, status=status.HTTP_200_OK)
