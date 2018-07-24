from rest_framework import serializers

from django.contrib.auth import get_user_model

from wirfi_app.models import UserProfile, BillingInfo, BusinessInfo, Device


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('user', 'phone_number', 'profile_picture')


class BusinessInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ('user', 'name', 'address', 'email', 'phone_number')


class BillingInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Billing
        fields = ('user', 'name', 'address', 'card_number', 'security_code', 'expiration_date')


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    billing = BillingInfoSerializer(read_only=True)
    business = BusinessInfoSerializer(read_only=True)

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'first_name', 'last_name', 'profile', 'billing', 'business',)


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
