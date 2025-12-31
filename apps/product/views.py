from rest_framework import viewsets, mixins, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import ProtectedError

from .models import Brand, Product, Supplier, Purchase
from .serializers import (
    BrandSerializer,
    ProductSerializer,
    SupplierSerializer,
    PurchaseSerializer,
    SkuGenerateSerializer,
    VoucherNumberGenerateSerializer,
)

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

    def destroy(self, request, *args, **kwargs):
        """
        Override destroy to handle ProtectedError and format it properly for drf_standardized_errors.
        """
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError as e:
            # Get the protected objects information
            protected_objects = list(e.protected_objects)
            if protected_objects:
                model_name = protected_objects[0].__class__._meta.verbose_name_plural
                raise ValidationError(
                    {
                        "detail": f"Cannot delete this brand because it is referenced by {len(protected_objects)} {model_name}."
                    }
                )
            raise ValidationError({"detail": "Cannot delete this brand because it is referenced by other objects."})


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

    def destroy(self, request, *args, **kwargs):
        """
        Override destroy to handle ProtectedError and format it properly for drf_standardized_errors.
        """
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError as e:
            # Get the protected objects information
            protected_objects = list(e.protected_objects)
            if protected_objects:
                model_name = protected_objects[0].__class__._meta.verbose_name_plural
                raise ValidationError(
                    {
                        "detail": f"Cannot delete this product because it is referenced by {len(protected_objects)} {model_name}."
                    }
                )
            raise ValidationError({"detail": "Cannot delete this product because it is referenced by other objects."})

    @extend_schema(
        summary="Generate SKU number",
        description="Generate a unique SKU number for a new product",
        responses={200: SkuGenerateSerializer},
    )
    @action(detail=False, methods=["get"], serializer_class=SkuGenerateSerializer, url_path="generate-sku")
    def generate_sku(self, request):
        """
        Generate a unique SKU number.
        Returns a unique SKU in the format: SKU-{YYYYMMDD}-{random_hex}
        """
        serializer = self.get_serializer(None)
        return Response(serializer.to_representation(None))


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

    def destroy(self, request, *args, **kwargs):
        """
        Override destroy to handle ProtectedError and format it properly for drf_standardized_errors.
        """
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError as e:
            # Get the protected objects information
            protected_objects = list(e.protected_objects)
            if protected_objects:
                model_name = protected_objects[0].__class__._meta.verbose_name_plural
                raise ValidationError(
                    {
                        "detail": f"Cannot delete this supplier because it is referenced by {len(protected_objects)} {model_name}."
                    }
                )
            raise ValidationError({"detail": "Cannot delete this supplier because it is referenced by other objects."})


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

    def destroy(self, request, *args, **kwargs):
        """
        Override destroy to handle ProtectedError and format it properly for drf_standardized_errors.
        """
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError as e:
            # Get the protected objects information
            protected_objects = list(e.protected_objects)
            if protected_objects:
                model_name = protected_objects[0].__class__._meta.verbose_name_plural
                raise ValidationError(
                    {
                        "detail": f"Cannot delete this purchase because it is referenced by {len(protected_objects)} {model_name}."
                    }
                )
            raise ValidationError({"detail": "Cannot delete this purchase because it is referenced by other objects."})

    @extend_schema(
        summary="Generate voucher number",
        description="Generate a unique voucher number for a new purchase",
        responses={200: VoucherNumberGenerateSerializer},
    )
    @action(detail=False, methods=["get"], serializer_class=VoucherNumberGenerateSerializer, url_path="generate-voucher-number")
    def generate_voucher_number(self, request):
        """
        Generate a unique voucher number.
        Returns a unique voucher number in the format: PAY-YYYY-0001 (PAY prefix, year, followed by sequential number)
        """
        serializer = self.get_serializer(None)
        return Response(serializer.to_representation(None))
