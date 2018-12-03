import re

from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from allauth.account import app_settings as allauth_settings
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from allauth.utils import email_address_exists

from rest_framework import serializers


def name_validator(value):
    if not re.match(r"^[A-Za-z\s]+$", value):
        raise serializers.ValidationError("Invalid field.")
    return value


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
        if re.match(settings.PASSWORD_VALIDATION_REGEX_PATTERN, password):
            return get_adapter().clean_password(password)

        raise serializers.ValidationError(
            _("Password must be 8 characters long with at least 1 number or 1 special character."))

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
