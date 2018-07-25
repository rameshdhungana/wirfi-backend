from rest_framework import serializers

from django.contrib.auth import get_user_model

from wirfi_app.models import Profile, Billing, Business, Device


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('user', 'phone_number', 'profile_picture')


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ('user', 'name', 'address', 'email', 'phone_number')


class BillingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Billing
        fields = ('user', 'name', 'address', 'card_number', 'security_code', 'expiration_date')


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    billing = BillingSerializer(read_only=True)
    business = BusinessSerializer(read_only=True)

    class Meta:
        model = get_user_model()
        fields = ('email', 'first_name', 'last_name', 'profile', 'billing', 'business',)


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        exclude = ('user',)
        read_only_fields = ['serial_number']


class DeviceSerialNoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ('id', 'serial_number')
        read_only_fields = ['name']
