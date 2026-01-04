from rest_framework import serializers
from apps.inventory.models import StockType


class StockTypeSerializer(serializers.ModelSerializer):
    total_ctn_quantity = serializers.ReadOnlyField()
    total_piece_quantity = serializers.ReadOnlyField()
    
    class Meta:
        model = StockType
        fields = [
            "id",
            "name",
            "total_ctn_quantity",
            "total_piece_quantity",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "total_ctn_quantity", "total_piece_quantity", "created_at", "updated_at")

