from rest_framework.routers import DefaultRouter

from .views import ColonyViewSet

router = DefaultRouter()
router.register('colonies', ColonyViewSet)

urlpatterns = router.urls
