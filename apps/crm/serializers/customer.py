from rest_framework import serializers
from apps.crm.models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    zone_name = serializers.CharField(source="zone.name", read_only=True)
    
    class Meta:
        model = Customer
        fields = [
            "id",
            "name",
            "shop_name",
            "contact_number",
            "address",
            "opening_balance",
            "zone",
            "zone_name",
            "due_limit",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "zone_name", "created_at", "updated_at")

