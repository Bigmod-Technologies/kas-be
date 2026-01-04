from rest_framework import viewsets, mixins, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Customer
from .serializers import CustomerSerializer
from apps.core.utils import DefaultPagination

# utils
from drf_spectacular.utils import extend_schema


@extend_schema(tags=["Customers"])
class CustomerViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    API endpoint that allows customers to be viewed or edited.
    """

    http_method_names = ["get", "post", "patch", "delete"]

    queryset = Customer.objects.select_related("zone").all()
    serializer_class = CustomerSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = [
        "name",
        "shop_name",
        "contact_number",
        "address",
    ]
    filterset_fields = [
        "zone",
    ]
    ordering_fields = ["name", "shop_name", "created_at"]
    ordering = ["name"]
