import hashlib

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode as uid_decoder

from rest_auth.serializers import PasswordResetConfirmSerializer
from rest_auth.views import PasswordResetConfirmView

from rest_framework import generics,status
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny 
from rest_framework.response import Response

from wirfi_app.models import UserActivationCode
from wirfi_app.views.password_change import valid_password_regex
from wirfi_app.serializers import PasswordResetSerializer, ResetPasswordMobileSerializer

User = get_user_model()


class ResetPasswordView(generics.CreateAPIView):
    """
    API to reset password that send email with reset link and activation code.

    Calls Django Auth PasswordResetForm save method.

    Accepts the following POST parameters: email
    Returns the success/fail message.
    """
    serializer_class = PasswordResetSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        try:
            user = User.objects.get(email=request.data['email'])
            activation_obj = UserActivationCode.objects.filter(user=user)

            if activation_obj:
                activation_code = get_activation_code(user, activation_obj[0].count)
                activation_obj.update(code=activation_code, count=activation_obj[0].count + 1, once_used=False)

            else:
                activation_code = get_activation_code(user, 0)
                activation_obj = UserActivationCode.objects.create(user=user, code=activation_code)

            # Create a serializer with request.data
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            # Return the success message with OK HTTP status
            return Response({
                "code": getattr(settings, 'SUCCESS_CODE', 1),
                "message": "Password reset e-mail has been sent. Please check your e-mail."
            }, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({
                "code": getattr(settings, 'ERROR_CODE', 0),
                "message": "Password reset e-mail has been sent. Please check your e-mail."
            }, status=status.HTTP_200_OK)


def get_activation_code(user, count):
    hash_string = "{uid}:{email}#{count}".format(uid=str(user.id), email=user.email, count=str(count + 1))
    return int(hashlib.sha256(hash_string.encode('utf-8')).hexdigest(), 16) % 10 ** 6


class ResetPasswordConfirmView(PasswordResetConfirmView):
    '''
    API to reset password using mailed link.
    '''
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs):
        if not valid_password_regex(request.data['new_password1']):
            return Response({
                "code": getattr(settings, 'ERROR_CODE', 0),
                "message": "Password must be 8 characters long with at least 1 number or 1 special character."
            }, status=status.HTTP_400_BAD_REQUEST)

        if not (request.data['new_password1'] == request.data['new_password2']):
            return Response({
                "code": getattr(settings, 'ERROR_CODE', 0),
                "message": "Passwords didn't match."
            }, status=status.HTTP_400_BAD_REQUEST)

        response = super().post(request, *args, **kwargs)
        UserActivationCode.objects.filter(user__email=request.data['email']).update(once_used=True)

        response.data = {
            "code": getattr(settings, 'SUCCESS_CODE', 1),
            "message": "Password has been successfully reset with new password."
        }
        return response


class ResetPasswordConfirmMobileView(generics.CreateAPIView):
    '''
    API to reset password from mobile using mailed activation code.
    '''
    serializer_class = ResetPasswordMobileSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        if not valid_password_regex(data['new_password1']):
            return Response({
                "code": getattr(settings, 'ERROR_CODE', 0),
                "message": "Password must be 8 characters long with at least 1 number or 1 special character."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = ResetPasswordMobileSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "code": getattr(settings, 'SUCCESS_CODE', 1),
            "message": "Password reset successfully done."
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
def validate_reset_password(request, uid, token):
    # Decode the uidb64 to uid to get User object
    try:
        uid = force_text(uid_decoder(uid))
        user = User.objects.get(pk=uid)
        if default_token_generator.check_token(user, token):
            data = {
                "code": getattr(settings, 'SUCCESS_CODE', 1),
                "message": "Password Reset Link is valid",
                "data": {
                    "email": user.email
                }
            }
        else:
            data = {
                "code": getattr(settings, 'ERROR_CODE', 0),
                "message": "Password Reset Link is Invalid",
            }
        return Response(data, status=status.HTTP_200_OK)

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        data = {
            "code": getattr(settings, 'ERROR_CODE', 0),
            "message": "Password Reset Link is Invalid",
        }
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
