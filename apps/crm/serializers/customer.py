from rest_framework import serializers
from apps.crm.models import Customer
from apps.area.serializers.area import AreaSerializer


class CustomerSerializer(serializers.ModelSerializer):
    area_details = AreaSerializer(source="area", read_only=True)
    
    class Meta:
        model = Customer
        fields = [
            "id",
            "customer_id",
            "name",
            "shop_name",
            "contact_number",
            "address",
            "opening_balance",
            "area",
            "area_details",
            "fridge_type",
            "due_limit",
            "order_discount_in_persentage",
            "have_special_discount",
            "special_discount_in_persentage",
            "due_sell",
            "due_collection",
            "balance",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "area_details",
            "due_sell",
            "due_collection",
            "balance",
            "created_at",
            "updated_at",
        )

