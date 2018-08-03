"""wirfi_web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views

from rest_framework_swagger.views import get_swagger_view

# from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token
# from rest_auth.registration.views import VerifyEmailView

from allauth.account.views import confirm_email as allauthemailconfirmation

schema_view = get_swagger_view(title='Wirfi API')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('list-api/', schema_view),
    path('', include('wirfi_app.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
