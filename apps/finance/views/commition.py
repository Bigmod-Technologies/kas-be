from rest_framework import viewsets, mixins, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.core.utils import DefaultPagination
from apps.finance.models import CommissionTransaction
from apps.finance.serializers import CommissionTransactionSerializer

from drf_spectacular.utils import extend_schema


@extend_schema(tags=["Commission Transactions"])
class CommissionTransactionViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    http_method_names = ["get", "post", "patch", "delete"]

    queryset = CommissionTransaction.objects.select_related("user").all()
    serializer_class = CommissionTransactionSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = [
        "user__username",
        "user__first_name",
        "user__last_name",
        "note",
    ]
    filterset_fields = {
        "user": ["exact", "in"],
        "transaction_date": ["exact", "gte", "lte"],
    }

    ordering_fields = ["transaction_date", "amount", "created_at"]
    ordering = ["-transaction_date", "-created_at"]
