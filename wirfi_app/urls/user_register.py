from django.urls import path, re_path
from wirfi_app.views import RegisterUserView, VerifyEmailRegisterView


urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='user_registration'),
    path('register/verify-email/', VerifyEmailRegisterView.as_view(), name="verify_email"),
    re_path('account-confirm-email/', VerifyEmailRegisterView.as_view(),
            name='account_email_verification_sent')
]