import django_filters

from .models import StockTransaction


class StockTransactionFilter(django_filters.FilterSet):
    """Filter stock transactions, including optional calendar-day range on ``created_at``."""

    date_from = django_filters.DateFilter(field_name="created_at", lookup_expr="date__gte")
    date_to = django_filters.DateFilter(field_name="created_at", lookup_expr="date__lte")

    class Meta:
        model = StockTransaction
        fields = [
            "transaction_type",
            "have_transfer",
            "stock_type",
            "stock_type__name",
            "product",
            "product_price",
            "order_item",
        ]
