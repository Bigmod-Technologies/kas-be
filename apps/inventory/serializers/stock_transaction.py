from rest_framework import serializers

from apps.inventory.models import StockTransaction, StockType
from apps.product.serializers import ProductPriceSerializer, ProductSerializer


class StockTypeNestedSerializer(serializers.ModelSerializer):
    """Nested serializer for stock type details."""

    class Meta:
        model = StockType
        fields = ["id", "name"]


class StockTransactionSerializer(serializers.ModelSerializer):
    """Serializer for stock transactions with nested details."""

    stock_type_details = StockTypeNestedSerializer(read_only=True, source="stock_type")
    product_details = ProductSerializer(read_only=True, source="product")
    product_price_details = ProductPriceSerializer(
        read_only=True, source="product_price"
    )
    transfer_from_details = StockTypeNestedSerializer(
        read_only=True, source="transfer_from"
    )
    transfer_to_details = StockTypeNestedSerializer(
        read_only=True, source="transfer_to"
    )

    class Meta:
        model = StockTransaction
        fields = [
            "id",
            "stock_type",
            "stock_type_details",
            "product",
            "product_details",
            "product_price",
            "product_price_details",
            "transaction_type",
            "ctn_quantity",
            "piece_quantity",
            "ctn_price",
            "piece_price",
            "total_price",
            "order_item",
            "damage_order_item",
            "free_offer_item",
            "have_transfer",
            "transfer_from",
            "transfer_from_details",
            "transfer_to",
            "transfer_to_details",
            "note",
            "batch_number",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "stock_type_details",
            "product_details",
            "product_price_details",
            "transfer_from_details",
            "transfer_to_details",
            "total_price",
            "created_at",
            "updated_at",
        )

    def validate(self, data):
        """Validate transfer fields when have_transfer is True."""
        have_transfer = data.get("have_transfer", False)
        transfer_from = data.get("transfer_from")
        transfer_to = data.get("transfer_to")

        if have_transfer:
            if not transfer_from or not transfer_to:
                raise serializers.ValidationError(
                    "Both transfer_from and transfer_to are required when have_transfer is True"
                )
            if transfer_from == transfer_to:
                raise serializers.ValidationError(
                    "transfer_from and transfer_to cannot be the same"
                )
        else:
            data["transfer_from"] = None
            data["transfer_to"] = None

        return data
