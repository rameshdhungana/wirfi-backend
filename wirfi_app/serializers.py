import stripe
import re

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model, authenticate
from django.conf import settings

from rest_framework import serializers, exceptions

from wirfi_app.models import Profile, Billing, Business, \
    Device, Industry, DeviceLocationHours, DeviceStatus, DeviceNetwork, \
    AuthorizationToken, DeviceSetting, DeviceNotification, PresetFilter, \
    DeviceCameraServices, UserActivationCode
from wirfi_app.forms import ResetPasswordForm

try:
    from allauth.account import app_settings as allauth_settings
    from allauth.account.adapter import get_adapter
    from allauth.account.utils import setup_user_email
    from allauth.utils import email_address_exists
except ImportError:
    raise ImportError("allauth needs to be added to INSTALLED_APPS.")

User = get_user_model()


def name_validator(value):
    if not re.match(r"^[A-Za-z]+$", value):
        raise serializers.ValidationError("Invalid field.")
    return value


def token_validator(value):
    if not re.match(r"^$|^[a-zA-Z0-9-]+$", value):
        raise serializers.ValidationError("Invalid field.")
    return value


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, allow_blank=False)
    password = serializers.CharField(style={'input_type': 'password'})
    device_id = serializers.CharField(allow_blank=True, validators=[token_validator])
    device_type = serializers.IntegerField()
    push_notification_token = serializers.CharField(allow_blank=True, validators=[token_validator])

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
    class Meta:
        model = Profile
        exclude = ('user',)
        read_only_fields = ('profile_picture',)

    def validate_address(self, address):
        if not re.match(r"^[-,A-Za-z0-9\s]+$", address):
            raise serializers.ValidationError("Invalid address.")
        return address

    def validate_phone_number(self, phone_number):
        if not re.match(r"^[-+0-9]+$", phone_number):
            raise serializers.ValidationError("Invalid phone number.")
        return phone_number


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        exclude = ('user',)


class BillingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Billing
        exclude = ('user', 'customer_id')


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()
    business = BusinessSerializer(read_only=True)
    billing = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'full_name', 'profile', 'business', 'billing')

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile')
        user = super().update(instance, validated_data)
        profile = Profile.objects.filter(user=user)
        if profile:
            profile_validated_data = UserProfileSerializer().validate(profile_data)
            profile_obj = UserProfileSerializer().update(profile.first(), profile_validated_data)
        else:
            serializer = UserProfileSerializer(data=profile_data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user)
            profile_obj = Profile.objects.get(pk=serializer.data['id'])
        user.profile = profile_obj
        return user

    def get_billing(self, obj):
        stripe.api_key = settings.STRIPE_API_KEY
        try:
            request = self.context.get("request")
            if request and hasattr(request, "user"):
                billing = Billing.objects.get(user=request.user)
                return stripe.Customer.retrieve(billing.customer_id)

        except:
            return None


class UserDetailsSerializer(serializers.ModelSerializer):
    """
    User model w/o password
    """

    class Meta:
        model = User
        fields = ('pk', 'email', 'first_name', 'last_name')
        read_only_fields = ('email',)


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


class DeviceNetworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceNetwork
        exclude = ('device',)


class DeviceLocationHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceLocationHours
        exclude = ('device',)


class DeviceStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceStatus
        exclude = ('id', 'device')
        read_only_fields = ('timestamp',)


class DeviceCameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceCameraServices
        exclude = ('device', 'id')


class IndustryTypeSerializer(serializers.ModelSerializer):
    is_user_created = serializers.SerializerMethodField()

    class Meta:
        model = Industry
        fields = ('id', 'name', 'is_user_created')

    def get_is_user_created(self, obj):
        return True if obj.user else False


class DeviceSerializer(serializers.ModelSerializer):
    industry_type = IndustryTypeSerializer(read_only=True)
    device_network = DeviceNetworkSerializer(read_only=True)
    location_hours = DeviceLocationHoursSerializer(many=True)
    device_settings = DeviceSettingSerializer(read_only=True)
    industry_type_id = serializers.CharField(allow_blank=True, write_only=True)
    camera_service = DeviceCameraSerializer(read_only=True, many=True)

    class Meta:
        model = Device
        exclude = ('user',)
        read_only_fields = ('location_logo', 'machine_photo')

    def create(self, validated_data):
        location_hours_data = validated_data.pop('location_hours', [])
        validated_data.pop('industry_type_id')
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


class DeviceSerializerForNotification(serializers.ModelSerializer):
    industry_type = IndustryTypeSerializer(read_only=True)

    class Meta:
        model = Device
        fields = ('id', 'name', 'industry_type', 'machine_photo')


class DeviceNotificationSerializer(serializers.ModelSerializer):
    device = DeviceSerializerForNotification(read_only=True)

    class Meta:
        model = DeviceNotification
        exclude = ('description',)


class ResetPasswordMobileSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    activation_code = serializers.CharField(max_length=6, write_only=True)
    new_password1 = serializers.CharField(max_length=64, write_only=True)
    new_password2 = serializers.CharField(max_length=64, write_only=True)

    def validate_activation_code(self, activation_code):
        if not re.match(r"^[0-9]+$", activation_code):
            raise serializers.ValidationError("Invalid activation code.")
        return activation_code

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if not email_address_exists(email) or not email:
                raise serializers.ValidationError(
                    _("A user with this e-mail address is not found."))
        return email

    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError(_("The two password fields didn't match."))
        return data

    def get_user_activation_model(self, data):
        activation_obj = UserActivationCode.objects.filter(code=data['activation_code'], user__email=data['email'], once_used=False)
        print(activation_obj)
        if not activation_obj:
            print("Activation code is invalid.")
            raise serializers.ValidationError(_("Activation code is invalid."))
        return activation_obj, activation_obj.first().user

    def create(self, validated_data):
        activation_obj, user = self.get_user_activation_model(validated_data)
        user.set_password(validated_data['new_password1'])
        user.save()
        activation_obj.update(once_used=True)
        return user


class UserRegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=64, validators=[name_validator])
    last_name = serializers.CharField(max_length=64, validators=[name_validator])
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


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset e-mail.
    """
    email = serializers.EmailField()

    password_reset_form_class = ResetPasswordForm

    def validate_email(self, value):
        # Create PasswordResetForm with the serializer
        self.reset_form = self.password_reset_form_class(data=self.initial_data)
        if not self.reset_form.is_valid():
            raise serializers.ValidationError(self.reset_form.errors)

        return value

    def save(self):
        request = self.context.get('request')
        # Set some values to trigger the send_email method.
        opts = {
            'use_https': request.is_secure(),
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
            'request': request,
            'email_template_name': 'reset_password.txt',
        }

        self.reset_form.save(**opts)


class PresetFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = PresetFilter
        exclude = ('user',)
