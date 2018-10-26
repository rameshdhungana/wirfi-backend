from django.urls import path, re_path

from wirfi_app.views import UserDetailView, dashboard_view, \
    BusinessView, BusinessDetailView, \
    BillingView, BillingDetailView, \
    IndustryTypeListView, IndustryTypeDetailView, LocationTypeListView, LocationTypeDetailView, \
    DeviceView, DeviceDetailView, DeviceNetworkView, DeviceNetworkDetailView, device_images_view, \
    add_device_status_view, device_priority_view, mute_device_view, DeviceSleepView, \
    DeviceCameraView, DeviceCameraDetailView, \
    Login, logout, RegisterUserView, VerifyEmailRegisterView, \
    ResetPasswordView, ResetPasswordConfirmView, ResetPasswordConfirmMobileView, ChangePasswordView, get_logged_in_user, \
    delete_billing_card, profile_images_view, validate_reset_password, \
    DeviceNotificationView, AllNotificationView, UpdateNotificationView, \
    PresetFilterView, PresetFilterDeleteView, CheckVersion

urlpatterns = [
    path('check-version/', CheckVersion.as_view()),
    
    path('dashboard/', dashboard_view, name='dashboard'),

    path('billing/', BillingView.as_view()),
    path('billing/<int:id>/', BillingDetailView.as_view()),

    path('business/', BusinessView.as_view()),
    path('business/<int:id>/', BusinessDetailView.as_view()),

    path('user/<int:id>/', UserDetailView.as_view(), name="user-detail"),
    path('user/<int:id>/image/', profile_images_view, name="user-image"),

    path('industry-type/', IndustryTypeListView.as_view(), name="industry-type"),
    path('industry-type/<int:id>/', IndustryTypeDetailView.as_view(), name="industry-type-detail"),

    path('location-type/', LocationTypeListView.as_view(), name="location-type"),
    path('location-type/<int:id>/', LocationTypeDetailView.as_view(), name="location-type-detail"),

    path('device/', DeviceView.as_view(), name="device-serial-number"),
    path('device/<int:id>/status/', add_device_status_view, name="device_status"),
    path('device/<int:id>/', DeviceDetailView.as_view(), name="device-detail"),
    path('device/<int:id>/images/', device_images_view, name="device-images"),
    path('device/<int:device_id>/network/', DeviceNetworkView.as_view(), name="device-network"),
    path('device/<int:device_id>/network/<int:id>/', DeviceNetworkDetailView.as_view(), name="device-network-detail"),
    path('device/<int:id>/mute/', mute_device_view, name='mute_device'),
    path('device/<int:id>/priority/', device_priority_view, name="device-priority"),
    path('device/<int:id>/sleep/', DeviceSleepView.as_view(), name="device-sleep"),
    path('device/<int:id>/camera/', DeviceCameraView.as_view()),
    path('device/<int:device_id>/camera/<int:pk>', DeviceCameraDetailView.as_view()),

    path('device/<int:device_id>/notification/', DeviceNotificationView.as_view(), name='device_notification'),
    path('notifications/', AllNotificationView.as_view(), name='all_notification'),
    path('notifications/<int:pk>/', UpdateNotificationView.as_view(), name='update_notification'),

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
    path('reset-password-mobile/', ResetPasswordConfirmMobileView.as_view(), name="reset_password_confirm_mobile"),

    path('change-password/', ChangePasswordView.as_view(), name="change-password"),
    path('me/', get_logged_in_user, name="me"),
    path('delete-billing-card/', delete_billing_card, )

]
