from rest_framework import viewsets, mixins, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import ProtectedError

from .models import OrderDelivery, OrderItem, DamageOrderItem, FreeOfferItem
from .serializers import (
    OrderDeliverySerializer,
    OrderNumberGenerateSerializer,
)
from apps.core.utils import DefaultPagination

# utils
from drf_spectacular.utils import extend_schema


@extend_schema(tags=["Orders"])
class OrderDeliveryViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    API endpoint that allows orders to be viewed or edited.
    Supports creating orders with items in a single request.
    """

    http_method_names = ["get", "post", "patch", "delete"]

    queryset = OrderDelivery.objects.select_related(
        "order_by"
    ).prefetch_related(
        "items__product", "items__price",
        "damage_items__product", "damage_items__price",
        "free_offer_items__product", "free_offer_items__price"
    ).all()
    serializer_class = OrderDeliverySerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["order_number", "order_by__username", "order_by__email"]
    filterset_fields = ["order_by", "order_date"]
    ordering_fields = ["order_date", "order_number", "cash_sell_amount", "created_at"]
    ordering = ["-order_date", "-created_at"]

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
                        "detail": f"Cannot delete this order because it is referenced by {len(protected_objects)} {model_name}."
                    }
                )
            raise ValidationError(
                {"detail": "Cannot delete this order because it is referenced by other objects."}
            )

    @extend_schema(
        summary="Generate order number",
        description="Generate a unique order number for a new order",
        responses={200: OrderNumberGenerateSerializer},
    )
    @action(
        detail=False,
        methods=["get"],
        serializer_class=OrderNumberGenerateSerializer,
        url_path="generate-order-number",
    )
    def generate_order_number(self, request):
        """
        Generate a unique order number.
        Returns a unique order number in the format: ORD-YYYY-0001 (ORD prefix, year, followed by sequential number)
        """
        serializer = self.get_serializer(None)
        return Response(serializer.to_representation(None))


