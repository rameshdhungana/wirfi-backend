from rest_framework import routers
from wirfi_app.views import UserApiView ,ProfileApiView, BusinessApiView, BillingApiView

router = routers.DefaultRouter()
router.register(r'user', UserApiView)
router.register(r'profile', ProfileApiView)
router.register(r'business', BusinessApiView)
router.register(r'billing', BillingApiView)

urlpatterns = []

urlpatterns += router.urls
