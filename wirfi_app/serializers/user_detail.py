import re

from rest_framework import serializers

from wirfi_app.models import Billing, Business, Profile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ('user',)
        read_only_fields = ('profile_picture',)

    def validate_address(self, address):
        if not re.match(r"^[-,A-Za-z0-9\s.]+$", address):
            raise serializers.ValidationError("Invalid address.")
        return address

    def validate_phone_number(self, phone_number):
        if not re.match(r"^[-+0-9]{10}$", phone_number):
            raise serializers.ValidationError("Invalid phone number.")
        return phone_number


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        exclude = ('user',)

    def validate_address(self, address):
        if not re.match(r"^[-,A-Za-z0-9\s.]+$", address):
            raise serializers.ValidationError("Invalid address.")
        return address

    def validate_phone_number(self, phone_number):
        if not re.match(r"^[-+0-9]{10}$", phone_number):
            raise serializers.ValidationError("Invalid phone number.")
        return phone_number


class BillingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Billing
        exclude = ('user', 'customer_id')


class UserPushNotificationSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('push_notifications',)