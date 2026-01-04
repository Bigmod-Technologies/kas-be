from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderDeliveryViewSet, SalesCollectionViewSet

router = DefaultRouter()
router.register(r"orders", OrderDeliveryViewSet)
router.register(r"sales-collections", SalesCollectionViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

