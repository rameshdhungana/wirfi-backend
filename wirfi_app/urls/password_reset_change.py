from django.urls import path, re_path
from wirfi_app.views import ResetPasswordView, validate_reset_password, ResetPasswordConfirmView, ResetPasswordConfirmMobileView, ChangePasswordView


urlpatterns = [
    path('reset-password/', ResetPasswordView.as_view(), name="reset-password"),
    path('validate-reset-password/<slug:uid>/<slug:token>/', validate_reset_password, name="validate_reset_password"),
    path('reset-password/confirm/', ResetPasswordConfirmView.as_view(), name="confirm-reset"),
    path('reset/<uidb64>/<token>/', ResetPasswordConfirmView.as_view(), name='password_reset_confirm'),
    path('reset-password-mobile/', ResetPasswordConfirmMobileView.as_view(), name="reset_password_confirm_mobile"),

    path('change-password/', ChangePasswordView.as_view(), name="change-password"),
]
