from rest_framework import viewsets, mixins, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Brand, Product, Supplier, Purchase
from .serializers import BrandSerializer, ProductSerializer, SupplierSerializer, PurchaseSerializer

from apps.core.utils import DefaultPagination


# utils
from drf_spectacular.utils import extend_schema


@extend_schema(tags=["Brands"])
class BrandViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    API endpoint that allows brands to be viewed or edited.
    """

    http_method_names = ["get", "post", "patch", "delete"]

    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["status"]
    ordering_fields = ["name"]

    ordering = ["-name"]


@extend_schema(tags=["Products"])
class ProductViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    API endpoint that allows products to be viewed or edited.
    """

    http_method_names = ["get", "post", "patch", "delete"]

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name", "sku", "status"]
    filterset_fields = ["status", "brand", "have_offer"]

    ordering_fields = ["name"]
    ordering = ["-name"]


@extend_schema(tags=["Suppliers"])
class SupplierViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    API endpoint that allows suppliers to be viewed or edited.
    """

    http_method_names = ["get", "post", "patch", "delete"]

    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["brand_name", "representative_name", "registration_number"]
    filterset_fields = ["status"]
    ordering_fields = ["brand_name", "created_at"]
    ordering = ["-created_at"]


@extend_schema(tags=["Purchases"])
class PurchaseViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    API endpoint that allows purchases to be viewed or edited.
    Supports creating purchases with items in a single request.
    """

    http_method_names = ["get", "post", "patch", "delete"]

    queryset = Purchase.objects.select_related("supplier").prefetch_related("items__product").all()
    serializer_class = PurchaseSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["voucher_number", "supplier__brand_name", "note"]
    filterset_fields = ["status", "supplier", "purchase_date"]
    ordering_fields = ["purchase_date", "total_amount", "created_at"]
    ordering = ["-purchase_date", "-created_at"]
