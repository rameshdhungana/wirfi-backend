from django.urls import path

from wirfi_app.views import impersonate_user, stop_impersonation


urlpatterns = [
    path('impersonate/<int:user_id>/', impersonate_user, name="impersonate-user"),
    path('impersonate/stop/', stop_impersonation, name="stop-impersonation")
]
