from django.urls import path
from wirfi_app.views import ping_server_from_wirfi_device

urlpatterns = [
    path('ping-server/', ping_server_from_wirfi_device)
]
