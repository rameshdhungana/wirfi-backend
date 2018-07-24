from django.urls import path
from rest_framework import routers
from wirfi_app.views import UserApiView, DeviceDetailView, DeviceSerialNoView

router = routers.DefaultRouter()
router.register(r'user', UserApiView)

urlpatterns = [
    path('device/', DeviceSerialNoView.as_view(), name="device-serial-number"),
    path('device/<int:id>/', DeviceDetailView.as_view(), name="device-detail")
]

urlpatterns += router.urls
