from rest_framework import serializers
from apps.sales.models import OrderDelivery, OrderItem, DamageOrderItem, FreeOfferItem
from apps.product.serializers import ProductSerializer, ProductPriceSerializer
from apps.user.serializers.staff import UserSerializer
from apps.sales.utils import generate_order_number


class OrderItemReadMixin(serializers.Serializer):
    """Mixin for shared read-only fields in order item serializers."""

    product_name = serializers.CharField(read_only=True, source="product.name")
    product_sku = serializers.CharField(read_only=True, source="product.sku")
    product_details = ProductSerializer(read_only=True, source="product")
    price_details = ProductPriceSerializer(read_only=True, source="price")
    total_amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )


class OrderItemSerializer(OrderItemReadMixin, serializers.ModelSerializer):
    """Serializer for OrderItem (nested in OrderDelivery)."""

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_sku",
            "product_details",
            "price",
            "price_details",
            "shift",
            "quantity_in_ctn",
            "quantity_in_pcs",
            "advanced_in_ctn",
            "advanced_in_pcs",
            "return_in_ctn",
            "return_in_pcs",
            "total_amount",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "product_name",
            "product_sku",
            "product_details",
            "price_details",
            "total_amount",
            "created_at",
            "updated_at",
        )


class OrderItemWriteSerializer(serializers.ModelSerializer):
    """Serializer for writing OrderItem data (nested in OrderDelivery)"""

    class Meta:
        model = OrderItem
        fields = [
            "product",
            "price",
            "shift",
            "quantity_in_ctn",
            "quantity_in_pcs",
            "advanced_in_ctn",
            "advanced_in_pcs",
            "return_in_ctn",
            "return_in_pcs",
        ]


class DamageOrderItemSerializer(OrderItemReadMixin, serializers.ModelSerializer):
    """Serializer for DamageOrderItem (nested in OrderDelivery)."""

    class Meta:
        model = DamageOrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_sku",
            "product_details",
            "price",
            "price_details",
            "quantity_in_ctn",
            "quantity_in_pcs",
            "damage_reason",
            "inventory_damage_deduction_percent",
            "total_amount",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "product_name",
            "product_sku",
            "product_details",
            "price_details",
            "total_amount",
            "created_at",
            "updated_at",
        )


class DamageOrderItemWriteSerializer(serializers.ModelSerializer):
    """Serializer for writing DamageOrderItem data (nested in OrderDelivery)"""

    class Meta:
        model = DamageOrderItem
        fields = [
            "product",
            "price",
            "quantity_in_ctn",
            "quantity_in_pcs",
            "damage_reason",
            "inventory_damage_deduction_percent",
        ]


class FreeOfferItemSerializer(OrderItemReadMixin, serializers.ModelSerializer):
    """Serializer for FreeOfferItem (nested in OrderDelivery)."""

    class Meta:
        model = FreeOfferItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_sku",
            "product_details",
            "price",
            "price_details",
            "quantity_in_ctn",
            "quantity_in_pcs",
            "total_amount",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "product_name",
            "product_sku",
            "product_details",
            "price_details",
            "total_amount",
            "created_at",
            "updated_at",
        )


class FreeOfferItemWriteSerializer(serializers.ModelSerializer):
    """Serializer for writing FreeOfferItem data (nested in OrderDelivery)"""

    class Meta:
        model = FreeOfferItem
        fields = [
            "product",
            "price",
            "quantity_in_ctn",
            "quantity_in_pcs",
        ]


class OrderDeliverySerializer(serializers.ModelSerializer):
    """Serializer for OrderDelivery with nested items"""

    order_by_details = UserSerializer(read_only=True, source="order_by")
    total_order_items = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    total_damage_items = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    total_free_offer_items = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    items = OrderItemSerializer(many=True, read_only=True)
    items_data = OrderItemWriteSerializer(
        many=True, write_only=True, required=False, allow_null=True
    )
    damage_items = DamageOrderItemSerializer(many=True, read_only=True)
    damage_items_data = DamageOrderItemWriteSerializer(
        many=True, write_only=True, required=False, allow_null=True
    )
    free_offer_items = FreeOfferItemSerializer(many=True, read_only=True)
    free_offer_items_data = FreeOfferItemWriteSerializer(
        many=True, write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = OrderDelivery
        fields = [
            "id",
            "order_number",
            "order_date",
            "order_by",
            "order_by_details",
            "cash_sell_amount",
            "priojon_offer",
            "total_order_items",
            "total_damage_items",
            "total_free_offer_items",
            "narration",
            "items",
            "items_data",
            "damage_items",
            "damage_items_data",
            "free_offer_items",
            "free_offer_items_data",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "order_number",
            "order_by_details",
            "total_order_items",
            "total_damage_items",
            "total_free_offer_items",
            "items",
            "damage_items",
            "free_offer_items",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):
        """Validate order and items_data"""
        items_data = attrs.get("items_data", []) or []
        damage_items_data = attrs.get("damage_items_data", []) or []
        free_offer_items_data = attrs.get("free_offer_items_data", []) or []

        if not self.instance and not items_data and not damage_items_data and not free_offer_items_data:
            raise serializers.ValidationError(
                {
                    "items_data": "At least one item (items, damage_items, or free_offer_items) is required to create an order"
                }
            )

        return attrs

    def _process_items(self, order, items_data, damage_items_data, free_offer_items_data):
        """Create order items. For update, pass empty lists to skip that item type."""
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        for item_data in damage_items_data:
            DamageOrderItem.objects.create(order=order, **item_data)
        for item_data in free_offer_items_data:
            FreeOfferItem.objects.create(order=order, **item_data)

    def create(self, validated_data):
        """Create order with items"""
        items_data = validated_data.pop("items_data", []) or []
        damage_items_data = validated_data.pop("damage_items_data", []) or []
        free_offer_items_data = validated_data.pop("free_offer_items_data", []) or []

        order = OrderDelivery.objects.create(**validated_data)
        self._process_items(order, items_data, damage_items_data, free_offer_items_data)
        return order

    def update(self, instance, validated_data):
        """Update order and handle items"""
        items_data = validated_data.pop("items_data", None)
        damage_items_data = validated_data.pop("damage_items_data", None)
        free_offer_items_data = validated_data.pop("free_offer_items_data", None)

        if items_data is not None or damage_items_data is not None or free_offer_items_data is not None:
            if items_data is not None:
                instance.items.all().delete()
            if damage_items_data is not None:
                instance.damage_items.all().delete()
            if free_offer_items_data is not None:
                instance.free_offer_items.all().delete()

            self._process_items(
                instance,
                items_data or [],
                damage_items_data or [],
                free_offer_items_data or [],
            )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class OrderNumberGenerateSerializer(serializers.Serializer):
    """
    Serializer for generating unique order numbers.
    Uses the generate_order_number utility function for order number generation logic.
    """

    order_number = serializers.CharField(read_only=True)

    def to_representation(self, instance):
        """
        Override to generate and return the order number using the utility function.
        """
        order_number = generate_order_number()
        return {"order_number": order_number}

