from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, CustomerDueReportViewSet

router = DefaultRouter()
router.register(r"customers", CustomerViewSet)
router.register(r"reports", CustomerDueReportViewSet, basename="customer-report")

urlpatterns = [
    path("", include(router.urls)),
]

