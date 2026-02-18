from rest_framework import serializers

from apps.sales.models import DueSell, DueCollection, OrderDelivery
from apps.crm.serializers.customer import CustomerSerializer
from apps.user.serializers.staff import UserSerializer


class OrderDeliveryBasicSerializer(serializers.ModelSerializer):
    """Basic serializer for OrderDelivery (used in nested serializers)"""

    class Meta:
        model = OrderDelivery
        fields = [
            "id",
            "order_number",
            "order_date",
        ]
        read_only_fields = [
            "id",
            "order_number",
            "order_date",
        ]


class DueSellSerializer(serializers.ModelSerializer):
    """Serializer for DueSell model."""

    customer_details = CustomerSerializer(read_only=True, source="customer")
    deliver_by_details = UserSerializer(read_only=True, source="deliver_by")
    order_details = OrderDeliveryBasicSerializer(read_only=True, source="order")
    order_number = serializers.SerializerMethodField()
    
    def get_order_number(self, obj):
        """Get order number if order exists"""
        return obj.order.order_number if obj.order else None

    class Meta:
        model = DueSell
        fields = [
            "id",
            "customer",
            "customer_details",
            "deliver_by",
            "deliver_by_details",
            "order",
            "order_details",
            "order_number",
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
            "order_details",
            "order_number",
            "created_at",
            "updated_at",
        ]


class DueSellWriteSerializer(serializers.ModelSerializer):
    """Write serializer for DueSell (used in bulk operations)."""

    class Meta:
        model = DueSell
        fields = [
            "customer",
            "deliver_by",
            "order",
            "sale_date",
            "amount",
            "note",
        ]


class DueSellBulkCreateSerializer(serializers.Serializer):
    """Serializer for bulk creating DueSell records."""

    due_sells = DueSellWriteSerializer(many=True)

    def create(self, validated_data):
        """Create multiple DueSell records."""
        due_sells_data = validated_data.pop("due_sells")
        created_due_sells = []
        
        for due_sell_data in due_sells_data:
            due_sell = DueSell.objects.create(**due_sell_data)
            created_due_sells.append(due_sell)
        
        return {"due_sells": created_due_sells}

    def to_representation(self, instance):
        """Return the created DueSell records."""
        return {
            "due_sells": DueSellSerializer(instance["due_sells"], many=True).data
        }


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


