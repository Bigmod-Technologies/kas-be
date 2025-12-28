from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BrandViewSet, ProductViewSet

router = DefaultRouter()
router.register(r"brands", BrandViewSet)
router.register(r"products", ProductViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
