from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StaffViewSet, DeliveryPersonViewSet

router = DefaultRouter()
router.register(r"staff", StaffViewSet)
router.register(r"delivery-persons", DeliveryPersonViewSet, basename="deliveryperson")

urlpatterns = [
    path("", include(router.urls)),
]

