import re

from django.conf import settings

from allauth.account import app_settings as allauth_settings
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from allauth.utils import email_address_exists

from rest_framework import serializers

from wirfi_app.forms import ResetPasswordForm
from wirfi_app.models import UserActivationCode


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
        activation_obj = UserActivationCode.objects.filter(code=data['activation_code'], user__email=data['email'],
                                                           once_used=False)
        if not activation_obj:
            raise serializers.ValidationError(_("Activation code is invalid."))
        return activation_obj, activation_obj.first().user

    def create(self, validated_data):
        activation_obj, user = self.get_user_activation_model(validated_data)
        user.set_password(validated_data['new_password1'])
        user.save()
        activation_obj.update(once_used=True)
        return user