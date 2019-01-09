from django.urls import path
from wirfi_app.views import DeviceStatusView, AllNotificationView, DeviceCameraDetailView, \
    DeviceCameraView, DeviceDetailView, DeviceNetworkDetailView, DeviceNetworkView, \
    DeviceSleepView, DeviceView, UpdateNotificationView, \
    device_images_view, mute_device_view, device_priority_view


urlpatterns = [
    path('device/', DeviceView.as_view(), name="device-serial-number"),
    path('device/<int:id>/', DeviceDetailView.as_view(), name="device-detail"),
    path('device/<int:id>/images/', device_images_view, name="device-images"),

    # informations
    path('device-status/', DeviceStatusView.as_view(), name="device_status"),
    path('device/<int:device_id>/network/', DeviceNetworkView.as_view(), name="device-network"),
    path('device/<int:device_id>/network/<int:id>/', DeviceNetworkDetailView.as_view(), name="device-network-detail"),

    # services
    path('device/<int:id>/camera/', DeviceCameraView.as_view()),
    path('device/<int:device_id>/camera/<int:pk>', DeviceCameraDetailView.as_view()),

    # settings
    path('device/<int:device_id>/mute/', mute_device_view, name='mute_device'),
    path('device/<int:device_id>/priority/', device_priority_view, name="device-priority"),
    path('device/<int:device_id>/sleep/', DeviceSleepView.as_view(), name="device-sleep"),

    # notification
    # path('device/<int:device_id>/notification/', DeviceNotificationView.as_view(), name='device_notification'),
    path('notifications/', AllNotificationView.as_view(), name='all_notification'),
    path('notifications/<int:pk>/', UpdateNotificationView.as_view(), name='update_notification'),


]
