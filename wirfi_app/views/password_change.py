import re

from django.conf import settings

from rest_auth.views import PasswordChangeView
from rest_auth.serializers import PasswordChangeSerializer

from rest_framework import status
from rest_framework.response import Response


def valid_password_regex(password):
    valid = re.match(settings.PASSWORD_VALIDATION_REGEX_PATTERN, password)
    return valid


class ChangePasswordView(PasswordChangeView):
    serializer_class = PasswordChangeSerializer

    def post(self, request, *args, **kwargs):
        if not valid_password_regex(request.data['new_password1']):
            return Response({
                "code": getattr(settings, 'ERROR_CODE', 0),
                "message": "Password must be 8 characters long with at least 1 number or 1 special character."
            }, status=status.HTTP_400_BAD_REQUEST)

        response = super().post(request, *args, **kwargs)
        response.data = {
            "code": getattr(settings, 'SUCCESS_CODE', 1),
            "message": "New password has been saved."
        }
        return response
