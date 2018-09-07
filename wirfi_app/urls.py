from django.urls import path, re_path

from rest_framework import routers

from wirfi_app.views import UserDetailView, dashboard_view, add_device_status_view, \
    BusinessView, BusinessDetailView, \
    BillingView, BillingDetailView, \
    IndustryTypeListView, IndustryTypeDetailView, \
    DeviceView, device_priority_view, DeviceDetailView, DeviceNetworkView, DeviceNetworkDetailView, device_images_view, \
    Login, logout, RegisterUserView, VerifyEmailRegisterView, \
    ResetPasswordView, ResetPasswordConfirmView, ChangePasswordView, get_logged_in_user, delete_billing_card, \
    profile_images_view, validate_reset_password, mute_device_view, DeviceNotificationView, AllNotificationView, \
    PresetFilterView, PresetFilterDeleteView

router = routers.DefaultRouter()
# router.register(r'profile', ProfileApiView)

urlpatterns = [
    path('dashboard/', dashboard_view, name='dashboard'),

    path('billing/', BillingView.as_view()),
    path('billing/<int:id>/', BillingDetailView.as_view()),

    path('business/', BusinessView.as_view()),
    path('business/<int:id>/', BusinessDetailView.as_view()),

    path('user/<int:id>/', UserDetailView.as_view(), name="user-detail"),
    path('user/<int:id>/image/', profile_images_view, name="user-image"),

    path('industry-type/', IndustryTypeListView.as_view(), name="industry-type"),
    path('industry-type/<int:id>/', IndustryTypeDetailView.as_view(), name="industry-type-detail"),

    path('device/', DeviceView.as_view(), name="device-serial-number"),
    path('device/<int:id>/status/', add_device_status_view, name="device_status"),
    path('device/<int:id>/', DeviceDetailView.as_view(), name="device-detail"),
    path('device/<int:id>/images/', device_images_view, name="device-images"),
    path('device/<int:id>/priority/', device_priority_view, name="device-priority"),
    path('device/<int:device_id>/network/', DeviceNetworkView.as_view(), name="device-network"),
    path('device/<int:device_id>/network/<int:id>/', DeviceNetworkDetailView.as_view(), name="device-network-detail"),
    path('device/<int:device_id>/mute/', mute_device_view, name='mute_device'),
    path('device/<int:device_id>/notification/', DeviceNotificationView.as_view(), name='device_notification'),
    path('device/notifications/', AllNotificationView.as_view(), name='all_notification'),

    path('preset-filter/', PresetFilterView.as_view()),
    path('preset-filter/<int:id>/', PresetFilterDeleteView.as_view()),

    path('login/', Login.as_view(), name='user_login'),
    path('logout/', logout, name='user_logout'),

    path('register/', RegisterUserView.as_view(), name='user_registration'),
    path('register/verify-email/', VerifyEmailRegisterView.as_view(), name="verify_email"),
    re_path('account-confirm-email/', VerifyEmailRegisterView.as_view(),
            name='account_email_verification_sent'),

    path('reset-password/', ResetPasswordView.as_view(), name="reset-password"),
    path('validate-reset-password/<slug:uid>/<slug:token>/', validate_reset_password, name="validate_reset_password"),

    path('reset-password/confirm/', ResetPasswordConfirmView.as_view(), name="confirm-reset"),
    path('reset/<uidb64>/<token>/', ResetPasswordConfirmView.as_view(), name='password_reset_confirm'),

    path('change-password/', ChangePasswordView.as_view(), name="change-password"),
    path('me/', get_logged_in_user, name="me"),
    path('delete-billing-card/', delete_billing_card, )

]

urlpatterns += router.urls
