from django.urls import path
from wirfi_app.views import dashboard_view, CheckVersion

urlpatterns = [
    path('check-version/', CheckVersion.as_view()),
    path('dashboard/', dashboard_view, name='dashboard'),
]