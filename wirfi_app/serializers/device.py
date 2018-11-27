from rest_framework import serializers

from wirfi_app.models import Device, DeviceLocationHours, DeviceSetting
from .industry_franchise_type import IndustryTypeSerializer, LocationTypeSerializer
from .device_information import DeviceLocationHoursSerializer, DeviceNetworkSerializer
from .device_services import DeviceCameraSerializer
from .device_settings import DeviceSettingSerializer


class DeviceSerializer(serializers.ModelSerializer):
    industry_type = IndustryTypeSerializer(read_only=True)
    location_type = LocationTypeSerializer(read_only=True)
    device_network = DeviceNetworkSerializer(read_only=True, many=True)
    location_hours = DeviceLocationHoursSerializer(many=True)
    device_settings = DeviceSettingSerializer(read_only=True)
    camera_service = DeviceCameraSerializer(read_only=True, many=True)
    industry_type_id = serializers.CharField(allow_blank=True, write_only=True)
    location_type_id = serializers.CharField(allow_blank=True, write_only=True)

    class Meta:
        model = Device
        exclude = ('user',)
        read_only_fields = ('location_logo', 'machine_photo')

    def to_representation(self, instance):
        device_network = {
            'primary_network': None,
            'secondary_network': None
        }
        data = super().to_representation(instance)
        data['machine_photo'] = data['machine_photo'][1:]
        data['location_logo'] = data['location_logo'][1:]
        if data['device_network']:
            for network in data['device_network']:
                network_dict = {'id': network['id'], 'ssid': network['ssid']}
                if network['primary_network']:
                    device_network['primary_network'] = network_dict
                else:
                    device_network['secondary_network'] = network_dict
        data['device_network'] = device_network
        return data

    def create(self, validated_data):
        location_hours_data = validated_data.pop('location_hours', [])
        validated_data.pop('industry_type_id')
        validated_data.pop('location_type_id')
        device = Device.objects.create(**validated_data)
        DeviceSetting.objects.create(device=device)

        for location_hour_data in location_hours_data:
            location_hour_data['device'] = device
            location_hour = DeviceLocationHours.objects.create(**location_hour_data)
            device.location_hours.add(location_hour)
        return device

    def update(self, instance, validated_data):
        location_hours_data = validated_data.pop('location_hours', [])
        device = super().update(instance, validated_data)

        for location_hour_data in location_hours_data:
            device_hour = DeviceLocationHours.objects.filter(device_id=device.id).get(
                day_id=location_hour_data['day_id'])
            validated_data = DeviceLocationHoursSerializer().validate(location_hour_data)
            location_hour = DeviceLocationHoursSerializer().update(device_hour, validated_data)
            device.location_hours.add(location_hour)
        return device