from rest_framework import serializers
from rest_auth.registration.serializers import RegisterSerializer
from rest_auth.serializers import LoginSerializer

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


class UserDetailsSerializer(serializers.ModelSerializer):
    """
    User model w/o password
    """

    class Meta:
        model = get_user_model()
        fields = ('pk', 'email', 'first_name', 'last_name')
        read_only_fields = ('email',)


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        exclude = ('user',)
        read_only_fields = ['serial_number']


class DeviceSerialNoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ('id', 'serial_number', 'name',)
        read_only_fields = ['name']


class UserRegistrationSerializer(RegisterSerializer):
    first_name = serializers.CharField(max_length=64)
    last_name = serializers.CharField(max_length=64)

    def get_cleaned_data(self):
        return {
            'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),

        }


class UserLoginSerializer(LoginSerializer):
    device_id = serializers.CharField(max_length=128)
    device_type = serializers.IntegerField()
    push_notification_token = serializers.CharField(max_length=128)
