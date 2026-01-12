from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ZoneViewSet, AreaViewSet

router = DefaultRouter()
router.register(r"zones", ZoneViewSet)
router.register(r"areas", AreaViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

