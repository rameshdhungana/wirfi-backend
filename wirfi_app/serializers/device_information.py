from rest_framework import serializers
from wirfi_app.models import DeviceLocationHours, DeviceNetwork, DeviceStatus


class DeviceLocationHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceLocationHours
        exclude = ('device',)


class DeviceNetworkSerializer(serializers.ModelSerializer):
    primary_network = serializers.BooleanField()

    class Meta:
        model = DeviceNetwork
        exclude = ('device',)
        write_only_fields = ('password',)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['ssid'] = data.pop('ssid_name')
        # data.pop('password')
        return data


class DeviceNetworkUpdateSerializer(DeviceNetworkSerializer):
    old_password = serializers.CharField(write_only=True)


class DeviceStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceStatus
        exclude = ('id', 'device')
        read_only_fields = ('timestamp',)
