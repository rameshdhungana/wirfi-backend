from django.urls import path, re_path

from rest_framework import routers

from wirfi_app.views import UserApiView, ProfileApiView, \
    BusinessView, BusinessDetailView, \
    BillingView, BillingDetailView, \
    DeviceView, DeviceDetailView, DeviceNetworkView, DeviceNetworkDetailView, DeviceLocationHoursView, \
    stripe_token_registration, \
    Login, logout, RegisterUserView, VerifyEmailRegisterView, \
    ResetPasswordView, ResetPasswordConfirmView, ChangePasswordView

router = routers.DefaultRouter()
router.register(r'user', UserApiView)
router.register(r'profile', ProfileApiView)

urlpatterns = [
    path('billing/', BillingView.as_view()),
    path('billing/<int:id>/', BillingDetailView.as_view()),

    path('business/', BusinessView.as_view()),
    path('business/<int:id>/', BusinessDetailView.as_view()),

    path('device/', DeviceView.as_view(), name="device-serial-number"),
    path('device/<int:id>/', DeviceDetailView.as_view(), name="device-detail"),
    path('device/<int:device_id>/network/', DeviceNetworkView.as_view(), name="device-network"),
    path('device/<int:device_id>/network/<int:id>/', DeviceNetworkDetailView.as_view(), name="device-network-detail"),
    path('device/<int:device_id>/location-hours/', DeviceLocationHoursView.as_view(), name="device-location-hours"),

    path('stripe/register-token/', stripe_token_registration, name="stripe_token_registration"),

    path('login/', Login.as_view(), name='user_login'),
    path('logout/', logout, name='user_logout'),

    path('register/', RegisterUserView.as_view(), name='user_registration'),
    path('register/verify-email/', VerifyEmailRegisterView.as_view(), name="verify_email"),
    re_path('account-confirm-email/', VerifyEmailRegisterView.as_view(),
            name='account_email_verification_sent'),

    path('reset-password/', ResetPasswordView.as_view(), name="reset-password"),
    path('reset-password/confirm/', ResetPasswordConfirmView.as_view(), name="confirm-reset"),
    path('reset/<uidb64>/<token>/', ResetPasswordConfirmView.as_view(), name='password_reset_confirm'),

    path('change-password/', ChangePasswordView.as_view(), name="change-password"),

]

urlpatterns += router.urls
