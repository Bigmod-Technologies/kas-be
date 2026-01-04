from rest_framework import viewsets, mixins, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import StockType, StockTransaction
from .serializers import StockTypeSerializer, StockTransactionSerializer
from apps.core.utils import DefaultPagination

# utils
from drf_spectacular.utils import extend_schema


@extend_schema(tags=["Stock Types"])
class StockTypeViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    API endpoint that allows stock types to be viewed or edited.
    """

    http_method_names = ["get"]

    queryset = StockType.objects.all()
    serializer_class = StockTypeSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["name"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]


@extend_schema(tags=["Stock Transactions"])
class StockTransactionViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    API endpoint that allows stock transactions to be viewed or edited.
    Supports creating transactions with IN/OUT types and transfers.
    """

    http_method_names = ["get", "post", "patch", "delete"]

    queryset = StockTransaction.objects.select_related(
        "stock_type", "product", "price", "transfer_from", "transfer_to"
    ).all()
    serializer_class = StockTransactionSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = [
        "product__name",
        "product__sku",
        "stock_type__name",
        "note",
    ]
    filterset_fields = [
        "transaction_type",
        "have_transfer",
        "stock_type",
        "product",
    ]
    ordering_fields = ["created_at", "transaction_type"]
    ordering = ["-created_at"]
