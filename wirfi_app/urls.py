from rest_framework import routers
from wirfi_app.views import UserApiView

router = routers.DefaultRouter()
router.register(r'tenant', UserApiView)

urlpatterns = []

urlpatterns += router.urls
