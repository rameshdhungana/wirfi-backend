from rest_framework import serializers
from wirfi_app.models import DeviceSetting


class DeviceMuteSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceSetting
        fields = ('is_muted', 'mute_start', 'mute_duration')
        read_only_fields = ['mute_start']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data = {
            "mute_settings": {
                "is_muted": data['is_muted'],
                "mute_start": data['mute_start'],
                "mute_duration": data["mute_duration"],
            }
        }
        return data


class DevicePrioritySettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceSetting
        fields = ('priority',)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data = {
            "priority_settings": {
                "priority": data['priority']
            }
        }
        return data


class DeviceSleepSerializer(serializers.ModelSerializer):
    sleep_duration = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = DeviceSetting
        fields = ('has_sleep_feature', 'is_asleep', 'sleep_start', 'sleep_duration')
        read_only_fields = ['has_sleep_feature', 'sleep_start']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data = {
            "sleep_settings": {
                "has_sleep_feature": data['has_sleep_feature'],
                "is_asleep": data['is_asleep'],
                "sleep_start": data['sleep_start'],
                "sleep_duration": data['sleep_duration']
            }
        }
        return data


class DeviceSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceSetting
        exclude = ('device', 'id')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data = {
            "mute_settings": {
                "is_muted": data['is_muted'],
                "mute_start": data['mute_start'],
                "mute_duration": data["mute_duration"],
            },
            "priority_settings": {
                "priority": data['priority']
            },
            "sleep_settings": {
                "has_sleep_feature": data['has_sleep_feature'],
                "is_asleep": data['is_asleep'],
                "sleep_start": data['sleep_start'],
                "sleep_duration": data['sleep_duration']
            }
        }
        return data