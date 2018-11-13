from rest_framework import serializers

from wirfi_app.models import DeviceCameraServices, DeviceNotification
from wirfi_app.serializers.device import DeviceSerializerForNotification


class DeviceCameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceCameraServices
        exclude = ('device', 'id')


class DeviceNotificationSerializer(serializers.ModelSerializer):
    device = DeviceSerializerForNotification(read_only=True)

    class Meta:
        model = DeviceNotification
        exclude = ('description',)