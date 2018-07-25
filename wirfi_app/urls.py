from django.urls import path

from rest_framework import routers

from wirfi_app.views import UserApiView, ProfileApiView, BusinessApiView, BillingApiView, DeviceDetailView, \
    DeviceSerialNoView, stripe_token_registration

router = routers.DefaultRouter()
router.register(r'user', UserApiView)
router.register(r'profile', ProfileApiView)
router.register(r'business', BusinessApiView)
router.register(r'billing', BillingApiView)

urlpatterns = [
    path('device/', DeviceSerialNoView.as_view(), name="device-serial-number"),
    path('device/<int:id>/', DeviceDetailView.as_view(), name="device-detail"),
    path('stripe/register-token/', stripe_token_registration, name="stripe_token_registration")
]

urlpatterns += router.urls
