import csv
from io import StringIO

from django.http import HttpResponse
from rest_framework import viewsets, mixins, filters
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
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

    queryset = Customer.objects.select_related("area", "area__zone").all()
    serializer_class = CustomerSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = [
        "customer_id",
        "name",
        "shop_name",
        "shop_name_en",
        "contact_number",
        "address",
    ]
    filterset_fields = {
        "area": ["exact", "in"],
        "fridge_type": ["exact"],
        "have_special_discount": ["exact"],
    }
    ordering_fields = ["name", "shop_name", "created_at"]
    ordering = ["name"]

    # def get_permissions(self):
    #     if self.action == "download_excel":
    #         return [AllowAny()]
    #     return [IsAuthenticated()]

    @extend_schema(
        summary="Download customers as Excel (CSV)",
        description="Export filtered customer list as CSV (opens in Excel). Uses CustomerSerializer.",
    )
    @action(detail=False, methods=["get"], url_path="download-excel")
    def download_excel(self, request):
        """Export customer data as CSV using CustomerSerializer. Respects list filters and search."""
        queryset = self.filter_queryset(self.get_queryset())
        data = CustomerSerializer(queryset, many=True).data

        # CSV columns: serializer fields, with area_details flattened to area_name
        csv_columns = [
            "customer_id",
            "shop_name",
            "name",
            "contact_number",
            "address",
            "area_name",  # flattened from area_details.name
            "due_limit",
            "opening_balance",
            "due_sell",
            "due_collection",
            "balance",
        ]
        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow(csv_columns)
        for row in data:
            area_details = row.pop("area_details", None)
            area_name = (area_details.get("name") or "") if area_details else ""
            flat_row = []
            for key in csv_columns:
                if key == "area_name":
                    flat_row.append(area_name)
                else:
                    value = row.get(key, "")
                    if value is None:
                        value = ""
                    flat_row.append(value)
            writer.writerow(flat_row)
        csv_content = buffer.getvalue()
        response = HttpResponse(
            "\ufeff" + csv_content,
            content_type="text/csv; charset=utf-8",
        )
        response["Content-Disposition"] = 'attachment; filename="customers.csv"'
        return response
