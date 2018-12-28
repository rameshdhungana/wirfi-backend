from rest_framework import serializers
from wirfi_app.models import Device, DeviceCameraServices, DeviceNotification


class DeviceCameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceCameraServices
        exclude = ('device', 'id')


class DeviceSerializerForNotification(serializers.ModelSerializer):

    class Meta:
        model = Device
        fields = ('id', 'name', 'machine_photo')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['machine_photo'] = data['machine_photo'][1:] if data['machine_photo'] else None
        return data


class DeviceNotificationSerializer(serializers.ModelSerializer):
    device = DeviceSerializerForNotification(read_only=True)

    class Meta:
        model = DeviceNotification
        exclude = ('description',)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['device']['device_status'] = data.pop('device_status')
        return data
