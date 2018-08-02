from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model, authenticate
from django.conf import settings

from rest_framework import serializers, exceptions
from rest_auth.registration.serializers import RegisterSerializer

from wirfi_app.models import Profile, Billing, Business, Device

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


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('user', 'phone_number', 'profile_picture')


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ('name', 'address', 'email', 'phone_number')


class BillingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Billing
        fields = ('name', 'address', 'card_number', 'security_code', 'expiration_date')


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    billing = BillingSerializer(read_only=True)
    business = BusinessSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'profile', 'billing', 'business',)


class UserDetailsSerializer(serializers.ModelSerializer):
    """
    User model w/o password
    """

    class Meta:
        model = User
        fields = ('pk', 'email', 'first_name', 'last_name')
        read_only_fields = ('email',)


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['id', 'name', 'serial_number', 'ssid_name', 'password']
        read_only_fields = ['serial_number', 'ssid_name', 'password']


class DeviceSerialNoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ('id', 'serial_number', 'name',)


class DeviceNetworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ('id', 'ssid_name', 'password',)


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

# class UserLoginSerializer(LoginSerializer):
#     device_id = serializers.CharField(max_length=128)
#     device_type = serializers.IntegerField()
#     push_notification_token = serializers.CharField(max_length=128)
