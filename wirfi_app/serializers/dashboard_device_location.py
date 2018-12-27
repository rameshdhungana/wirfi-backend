from rest_framework import serializers

from wirfi_app.models import Device


class DeviceLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ('id', 'latitude', 'longitude')
