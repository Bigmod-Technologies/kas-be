from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StockTypeViewSet, StockTransactionViewSet

router = DefaultRouter()
router.register(r"stock-types", StockTypeViewSet)
router.register(r"stock-transactions", StockTransactionViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
