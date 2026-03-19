from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StockTypeViewSet, StockTransactionViewSet, StockTypeReportView

router = DefaultRouter()
router.register(r"stock-types", StockTypeViewSet)
router.register(r"stock-transactions", StockTransactionViewSet)

urlpatterns = [
    path("stock-type-report/", StockTypeReportView.as_view(), name="stock-type-report"),
    path("", include(router.urls)),
]
