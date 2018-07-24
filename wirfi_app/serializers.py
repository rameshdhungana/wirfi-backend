from rest_framework import serializers
from django.conf import settings

from wirfi_app.models import UserProfile, BillingInfo, BusinessInfo, Device


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('user', 'phone_number')


class BillingInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingInfo
        fields = ('user', 'name', 'address', 'email', 'phone_number')


class BusinessInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessInfo
        fields = ('user', 'name', 'address', 'security_code', 'expiration_code')


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(many=True)
    billing = BillingInfoSerializer(many=True)
    business = BusinessInfoSerializer(many=True)

    class Meta:
        model = settings.AUTH_USER_MODEL
        fields = ('username', 'email', 'first_name', 'last_name', 'profile', 'billing', 'business')


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        exclude = ('serial_number', 'user',)
        read_only_fields = ['serial_number']


class DeviceSerialNoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ('id', 'serial_number')
        read_only_fields = ['name']
