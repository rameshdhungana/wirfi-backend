import re

from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


from allauth.account import app_settings as allauth_settings
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from allauth.utils import email_address_exists

from rest_framework import serializers

User = get_user_model()


class AdminUserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(max_length=128, write_only=True)
    password2 = serializers.CharField(max_length=128, write_only=True)

    class Meta:
        model = User
        fields = ('pk', 'first_name', 'last_name', 'email', 'password1', 'password2', 'is_superuser', 'is_staff')
        read_only_fields = ('is_superuser',)
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False}
        }

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

    def save(self, request):
        self.validated_data['password'] = self.validated_data.pop('password1')
        self.validated_data.pop('password2')
        user = User.objects.create_user(**self.validated_data)
        setup_user_email(request, user, [])
        return user
