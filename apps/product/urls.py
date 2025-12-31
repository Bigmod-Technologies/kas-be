from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BrandViewSet, ProductViewSet, SupplierViewSet, PurchaseViewSet

router = DefaultRouter()
router.register(r"brands", BrandViewSet)
router.register(r"items", ProductViewSet)
router.register(r"suppliers", SupplierViewSet)
router.register(r"purchases", PurchaseViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
