from django.urls import path
from wirfi_app.views import ping_server_from_wirfi_device, set_device_primary_network_settings

urlpatterns = [
    # this api is called by device every minute with device information and tasks for device are sent
    #  as device response
    path('server/ping/', ping_server_from_wirfi_device),

]
