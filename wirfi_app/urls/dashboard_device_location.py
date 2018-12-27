from django.urls import path

from wirfi_app.views import DeviceLocation

urlpatterns = [
    # latlong locations of devices per user for route planning
    path('device/locations/', DeviceLocation.as_view(), name='device_location'),

]
