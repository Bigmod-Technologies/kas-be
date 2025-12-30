from rest_framework import viewsets, mixins, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Brand, Product, Supplier
from .serializers import BrandSerializer, ProductSerializer, SupplierSerializer

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
