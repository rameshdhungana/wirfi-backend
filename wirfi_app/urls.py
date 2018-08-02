from django.urls import path

from rest_framework import routers

from wirfi_app.views import UserApiView, ProfileApiView, BusinessApiView, BillingView, BillingDetailView, \
    DeviceDetailView, DeviceSerialNoView, DeviceNetworkView, stripe_token_registration, RegisterUser, Login,VerifyEmailView

router = routers.DefaultRouter()
router.register(r'user', UserApiView)
router.register(r'profile', ProfileApiView)
router.register(r'business', BusinessApiView)

urlpatterns = [
    path('billing/', BillingView.as_view()),
    path('billing/<int:id>/', BillingDetailView.as_view()),
    path('device/', DeviceSerialNoView.as_view(), name="device-serial-number"),
    path('device/<int:id>/', DeviceDetailView.as_view(), name="device-detail"),
    path('device/<int:id>/network/', DeviceNetworkView.as_view(), name="device-network"),
    path('stripe/register-token/', stripe_token_registration, name="stripe_token_registration"),
    path('register/', RegisterUser.as_view(), name='user_registration'),
    path('login/', Login.as_view(), name='user_login'),
    path('api/auth/registration/account-confirm-email/(?P<key>[-:\w]+)/$', VerifyEmailView.as_view(),
         name='account_confirm_email'),
]

urlpatterns += router.urls
