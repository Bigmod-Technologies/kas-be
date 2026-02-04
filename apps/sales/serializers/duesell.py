from rest_framework import serializers

from apps.sales.models import DueSell, DueCollection
from apps.crm.serializers.customer import CustomerSerializer
from apps.user.serializers.staff import UserSerializer


class DueSellSerializer(serializers.ModelSerializer):
    """Serializer for DueSell model."""

    customer_details = CustomerSerializer(read_only=True, source="customer")
    deliver_by_details = UserSerializer(read_only=True, source="deliver_by")

    class Meta:
        model = DueSell
        fields = [
            "id",
            "customer",
            "customer_details",
            "deliver_by",
            "deliver_by_details",
            "sale_date",
            "amount",
            "note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "customer_details",
            "deliver_by_details",
            "created_at",
            "updated_at",
        ]


class DueCollectionSerializer(serializers.ModelSerializer):
    """Serializer for DueCollection model."""

    customer_details = CustomerSerializer(read_only=True, source="customer")
    collected_by_details = UserSerializer(read_only=True, source="collected_by")

    class Meta:
        model = DueCollection
        fields = [
            "id",
            "customer",
            "customer_details",
            "collected_by",
            "collected_by_details",
            "collection_date",
            "amount",
            "note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "customer_details",
            "collected_by_details",
            "created_at",
            "updated_at",
        ]


