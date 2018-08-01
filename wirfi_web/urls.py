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
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings

from rest_framework_swagger.views import get_swagger_view
# from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token

schema_view = get_swagger_view(title='Wirfi API')
# from .swagger_schema import schema_view

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('list-api', schema_view),
                  path('api/auth/', include('rest_auth.urls')),
                  path('api/auth/registration/', include('rest_auth.registration.urls')),
                  path('', include('wirfi_app.urls')),
                  # path('api-token-auth/', obtain_jwt_token),
                  # path('api-token-refresh/', refresh_jwt_token),
                  # path('api-token-verify/', verify_jwt_token),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
