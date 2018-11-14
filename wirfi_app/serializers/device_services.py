from rest_framework import serializers

from wirfi_app.models import Device, DeviceCameraServices, DeviceNotification
from .industry_franchise_type import IndustryTypeSerializer


class DeviceCameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceCameraServices
        exclude = ('device', 'id')


class DeviceSerializerForNotification(serializers.ModelSerializer):
    industry_type = IndustryTypeSerializer(read_only=True)

    class Meta:
        model = Device
        fields = ('id', 'name', 'industry_type', 'machine_photo')


class DeviceNotificationSerializer(serializers.ModelSerializer):
    device = DeviceSerializerForNotification(read_only=True)

    class Meta:
        model = DeviceNotification
        exclude = ('description',)