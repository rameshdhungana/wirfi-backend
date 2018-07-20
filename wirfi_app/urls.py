from rest_framework import routers
from wirfi_app.views import UserApiView

router = routers.DefaultRouter()
router.register(r'user', UserApiView)

urlpatterns = []

urlpatterns += router.urls
