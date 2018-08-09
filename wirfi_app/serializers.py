from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model, authenticate
from django.conf import settings

from rest_framework import serializers, exceptions
# from rest_auth.registration.serializers import RegisterSerializer

from wirfi_app.models import Profile, Billing, Business, \
    Device, DeviceLocationHours, DeviceNetwork, \
    AuthorizationToken

try:
    from allauth.account import app_settings as allauth_settings
    from allauth.account.adapter import get_adapter
    from allauth.account.utils import setup_user_email
    from allauth.utils import email_address_exists
except ImportError:
    raise ImportError("allauth needs to be added to INSTALLED_APPS.")

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, allow_blank=False)
    password = serializers.CharField(style={'input_type': 'password'})
    device_id = serializers.CharField(allow_blank=True)
    device_type = serializers.IntegerField()
    push_notification_token = serializers.CharField(allow_blank=True)

    def _validate_email(self, email, password):
        user = None
        if email and password:
            user = authenticate(email=email, password=password)
        else:
            msg = _('Must include "email" and "password".')
            raise exceptions.ValidationError(msg)
        return user

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = None

        if 'allauth' in settings.INSTALLED_APPS:
            from allauth.account import app_settings

            # Authentication through email
            if app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.EMAIL:
                user = self._validate_email(email, password)

        # Did we get back an active user?
        if user:
            if not user.is_active:
                msg = _('User account is disabled.')
                raise exceptions.ValidationError(msg)
        else:
            msg = _('Unable to log in with provided credentials.')
            raise exceptions.ValidationError(msg)

        # If required, is the email verified?
        if 'rest_auth.registration' in settings.INSTALLED_APPS:
            from allauth.account import app_settings
            if app_settings.EMAIL_VERIFICATION == app_settings.EmailVerificationMethod.MANDATORY:
                email_address = user.emailaddress_set.get(email=user.email)
                if not email_address.verified:
                    raise serializers.ValidationError(_('E-mail is not verified.'))

        attrs['user'] = user
        return attrs


class AuthorizationTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthorizationToken
        exclude = ('user',)


class UserProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField()

    class Meta:
        model = Profile
        fields = '__all__'
        read_only_fields = ('user',)


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        exclude = ('user',)


class BillingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Billing
        exclude = ('user', 'stripe_token', 'customer_id')


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    billing = BillingSerializer(read_only=True)
    business = BusinessSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'profile', 'billing', 'business',)


class UserDetailsSerializer(serializers.ModelSerializer):
    """
    User model w/o password
    """

    class Meta:
        model = User
        fields = ('pk', 'email', 'first_name', 'last_name')
        read_only_fields = ('email',)


class DeviceNetworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceNetwork
        exclude = ('device',)


class DeviceLocationHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceLocationHours
        exclude = ('device',)


class DeviceSerializer(serializers.ModelSerializer):
    network = DeviceNetworkSerializer(read_only=True)
    location_hours = DeviceLocationHoursSerializer(many=True)

    class Meta:
        model = Device
        exclude = ('user',)
        read_only_fields = ('location_logo', 'machine_photo',)

    def create(self, validated_data):
        location_hours_data = validated_data.pop('location_hours', [])
        device = Device.objects.create(**validated_data)

        for location_hour_data in location_hours_data:
            location_hour_data['device'] = device
            location_hour = DeviceLocationHours.objects.create(**location_hour_data)
            device.location_hours.add(location_hour)
        return device

    def update(self, instance, validated_data):
        location_hours_data = validated_data.pop('location_hours', [])
        device = super().update(instance, validated_data)

        for location_hour_data in location_hours_data:
            device_hour = DeviceLocationHours.objects.filter(device_id=device.id).get(day_id=location_hour_data['day_id'])
            validated_data = DeviceLocationHoursSerializer().validate(location_hour_data)
            location_hour = DeviceLocationHoursSerializer().update(device_hour, validated_data)
            device.location_hours.add(location_hour)
        return device


class UserRegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=64)
    last_name = serializers.CharField(max_length=64)
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise serializers.ValidationError(
                    _("A user is already registered with this e-mail address."))
        return email

    def validate_password1(self, password):
        return get_adapter().clean_password(password)

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError(_("The two password fields didn't match."))
        return data

    def custom_signup(self, request, user):
        pass

    def get_cleaned_data(self):
        return {
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user
