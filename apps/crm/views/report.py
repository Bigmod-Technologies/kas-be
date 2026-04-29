from decimal import Decimal

from django.db.models import CharField, F, Sum, UUIDField, Value
from django.shortcuts import get_object_or_404
from django.db.models.functions import Concat
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema, OpenApiParameter

from apps.core.utils import DefaultPagination
from apps.crm.models import Customer
from apps.crm.serializers import (
    CustomerDueReportFilterSerializer,
    CustomerDueReportItemSerializer,
)
from apps.sales.models import DueSell, DueCollection


@extend_schema(
    tags=["Customer Reports"],
    description=(
        "Get merged DueSell(due_sell) and DueCollection(due_collection) entries for one customer. "
        "Supports date range filtering and pagination."
    ),
    parameters=[
        OpenApiParameter(
            name="customer",
            description="Customer UUID",
            required=True,
            type=str,
        ),
        OpenApiParameter(
            name="start_date",
            description="Start date (YYYY-MM-DD)",
            required=False,
            type=str,
        ),
        OpenApiParameter(
            name="end_date",
            description="End date (YYYY-MM-DD)",
            required=False,
            type=str,
        ),
        OpenApiParameter(
            name="page",
            description="Page number",
            required=False,
            type=int,
        ),
        OpenApiParameter(
            name="page_size",
            description="Items per page",
            required=False,
            type=int,
        ),
    ],
)
class CustomerDueReportViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Merged due report for a specific customer.
    Combines DueSell and DueCollection records in a single paginated timeline.
    """

    http_method_names = ["get"]
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination
    queryset = Customer.objects.none()
    serializer_class = CustomerDueReportItemSerializer

    def list(self, request, *args, **kwargs):
        filter_serializer = CustomerDueReportFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        filters = filter_serializer.validated_data

        customer = get_object_or_404(Customer, id=filters["customer"])
        start_date = filters.get("start_date")
        end_date = filters.get("end_date")

        due_sell_qs = DueSell.objects.select_related("deliver_by", "order").filter(
            customer=customer
        )
        due_collection_qs = DueCollection.objects.select_related("collected_by").filter(
            customer=customer
        )

        if start_date:
            due_sell_qs = due_sell_qs.filter(sale_date__gte=start_date)
            due_collection_qs = due_collection_qs.filter(
                collection_date__gte=start_date
            )

        if end_date:
            due_sell_qs = due_sell_qs.filter(sale_date__lte=end_date)
            due_collection_qs = due_collection_qs.filter(collection_date__lte=end_date)

        due_sell_entries = (
            due_sell_qs.order_by()
            .annotate(
                entry_type=Value("due_sell", output_field=CharField()),
                entry_date=F("sale_date"),
                performed_by=Concat(
                    F("deliver_by__first_name"),
                    Value(" "),
                    F("deliver_by__last_name"),
                    output_field=CharField(),
                ),
                order_number=F("order__order_number"),
            )
            .values(
                "id",
                "entry_type",
                "entry_date",
                "amount",
                "note",
                "performed_by",
                "order_id",
                "order_number",
                "created_at",
            )
        )

        due_collection_entries = (
            due_collection_qs.order_by()
            .annotate(
                entry_type=Value("due_collection", output_field=CharField()),
                entry_date=F("collection_date"),
                performed_by=Concat(
                    F("collected_by__first_name"),
                    Value(" "),
                    F("collected_by__last_name"),
                    output_field=CharField(),
                ),
                order_id=Value(None, output_field=UUIDField()),
                order_number=Value(None, output_field=CharField()),
            )
            .values(
                "id",
                "entry_type",
                "entry_date",
                "amount",
                "note",
                "performed_by",
                "order_id",
                "order_number",
                "created_at",
            )
        )

        merged_entries_qs = due_sell_entries.union(
            due_collection_entries, all=True
        ).order_by("-entry_date", "-created_at")

        period_due_sell = due_sell_qs.aggregate(total=Sum("amount"))[
            "total"
        ] or Decimal("0.00")
        period_due_collection = due_collection_qs.aggregate(total=Sum("amount"))[
            "total"
        ] or Decimal("0.00")

        page = self.paginate_queryset(merged_entries_qs)
        serializer = self.get_serializer(page, many=True)
        paginated_response = self.get_paginated_response(serializer.data)
        paginated_response.data["customer"] = {
            "id": str(customer.id),
            "customer_id": customer.customer_id,
            "name": customer.name,
            "shop_name": customer.shop_name,
            "contact_number": customer.contact_number,
            "address": customer.address,
        }
        paginated_response.data["summary"] = {
            "opening_balance": customer.opening_balance,
            "period_due_sell": period_due_sell,
            "period_due_collection": period_due_collection,
            "period_net_change": period_due_collection - period_due_sell,
            "current_balance": customer.balance,
        }
        paginated_response.data["date_range"] = {
            "start_date": start_date,
            "end_date": end_date,
        }
        return paginated_response
