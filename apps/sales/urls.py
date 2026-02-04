from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderDeliveryViewSet, DueSellViewSet, DueCollectionViewSet

router = DefaultRouter()
router.register(r"orders", OrderDeliveryViewSet)
router.register(r"due-sells", DueSellViewSet)
router.register(r"due-collections", DueCollectionViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

