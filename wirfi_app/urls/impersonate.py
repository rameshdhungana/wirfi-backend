from django.urls import path

from wirfi_app.views import impersonate_user


urlpatterns = [
    path('impersonate/<int:user_id>/', impersonate_user, name="impersonate-user"),
]
