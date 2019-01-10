from django.conf import settings
from django.db.models import Q

from rest_framework import generics, status
from rest_framework.response import Response

from wirfi_app.models import Device, DeviceNotification, NOTIFICATION_TYPE, READ
from wirfi_app.models.device_services import URGENT_UNREAD, UNREAD
from wirfi_app.serializers import DeviceNotificationSerializer


class AllNotificationView(generics.ListAPIView):
    '''
    API to list logged in User's notifications
    '''
    serializer_class = DeviceNotificationSerializer

    def get_each_type_queryset(self, type):
        return DeviceNotification.objects.filter(device__user=self.request.user).filter(type=type).order_by('-id')

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


# class DeviceNotificationView(generics.CreateAPIView):
#     serializer_class = DeviceNotificationSerializer
#
#     def get_each_type_queryset(self, type):
#         return DeviceNotification.objects.filter(device_id=self.kwargs['device_id'], type=type).order_by('-id')
#
#     def create(self, request, *args, **kwargs):
#         device = Device.objects.get(pk=self.kwargs['device_id'])
#         serializer = DeviceNotificationSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save(device=device)
#         data = {
#             "code": getattr(settings, 'SUCCESS_CODE', 1),
#             'message': "Device Notifications created successfully",
#             "data": serializer.data
#         }
#         return Response(data, status=status.HTTP_200_OK)


class UpdateNotificationView(generics.UpdateAPIView):  # , generics.DestroyAPIView):
    '''
    API to update notification status type (Urgent Unread/Unread -> Read)
    '''
    serializer_class = DeviceNotificationSerializer
    queryset = DeviceNotification.objects.filter(Q(type=URGENT_UNREAD) | Q(type=UNREAD))

    def update(self, request, *args, **kwargs):
        notifications = self.get_queryset().filter(device=self.get_object().device)
        for notification in notifications:
            notification.type = READ
            notification.save()
        data = {
            "code": getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Notifications is updated to READ Type successfully",
        }
        return Response(data, status=status.HTTP_200_OK)

    # def destroy(self, request, *args, **kwargs):
    #     self.get_object().delete()
    #     return Response({
    #         "code": getattr(settings, 'SUCCESS_CODE', 1),
    #         "message": "Successfully deleted notification."
    #     }, status=status.HTTP_200_OK)
