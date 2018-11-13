from rest_framework import serializers


class CheckVersionSerializer(serializers.Serializer):
    device_type = serializers.CharField(required=True, max_length=1)
    app_version = serializers.CharField(required=True, max_length=15)