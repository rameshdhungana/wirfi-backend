from django.conf import settings

from allauth.account import app_settings as allauth_settings
from allauth.account.utils import complete_signup
from rest_auth.registration.views import RegisterView, VerifyEmailView, VerifyEmailSerializer

from wirfi_app.models import AuthorizationToken
from wirfi_app.serializers import UserRegistrationSerializer


class RegisterUserView(RegisterView):
    serializer_class = UserRegistrationSerializer
    token_model = AuthorizationToken

    def get_response_data(self, user):
        if allauth_settings.EMAIL_VERIFICATION == \
                allauth_settings.EmailVerificationMethod.MANDATORY:
            data = {
                'code': getattr(settings, 'SUCCESS_CODE', 1),
                'message': "Please check your email for account validation link. Thank you.",
            }
            return data

    def perform_create(self, serializer):
        user = serializer.save(self.request)
        complete_signup(self.request._request, user,
                        allauth_settings.EMAIL_VERIFICATION,
                        None)
        return user


class VerifyEmailRegisterView(VerifyEmailView):
    serializer_class = VerifyEmailSerializer

    def post(self, request, *args, **kwargs):
        response = super(VerifyEmailRegisterView, self).post(request, *args, **kwargs)
        response.data = {
            "code": getattr(settings, 'SUCCESS_CODE', 1),
            "message": "Email Successfully verified."
        }
        return response
