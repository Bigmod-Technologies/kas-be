from rest_framework import serializers
from decimal import Decimal
from apps.sales.models import OrderDelivery, OrderItem
from apps.product.serializers import ProductSerializer, ProductPriceSerializer
from apps.user.serializers.staff import UserSerializer
from apps.sales.utils import generate_order_number


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderItem (nested in OrderDelivery)"""

    product_name = serializers.CharField(read_only=True, source="product.name")
    product_sku = serializers.CharField(read_only=True, source="product.sku")
    product_details = ProductSerializer(read_only=True, source="product")
    price_details = ProductPriceSerializer(read_only=True, source="price")
    total_amount = serializers.SerializerMethodField()

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

    def get_total_amount(self, obj):
        """Calculate total amount for this order item"""
        if not obj.price:
            return Decimal("0.00")

        total = Decimal("0.00")

        # Calculate net quantity (quantity + advanced - return)
        net_ctn = obj.quantity_in_ctn + obj.advanced_in_ctn - obj.return_in_ctn
        net_pcs = obj.quantity_in_pcs + obj.advanced_in_pcs - obj.return_in_pcs

        # Calculate amount for cartons (handles both positive and negative net quantities)
        if obj.price.ctn_price and net_ctn != 0:
            total += Decimal(str(net_ctn)) * obj.price.ctn_price

        # Calculate amount for pieces (handles both positive and negative net quantities)
        if obj.price.piece_price and net_pcs != 0:
            total += Decimal(str(net_pcs)) * obj.price.piece_price

        return total


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


class OrderDeliverySerializer(serializers.ModelSerializer):
    """Serializer for OrderDelivery with nested items"""

    order_by_details = UserSerializer(read_only=True, source="order_by")
    items = OrderItemSerializer(many=True, read_only=True)
    items_data = OrderItemWriteSerializer(
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
            "total_amount",
            "items",
            "items_data",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "order_number",
            "order_by_details",
            "items",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):
        """Validate order and items_data"""
        items_data = attrs.get("items_data", []) or []

        # Validate that items_data is provided for create
        if not self.instance and not items_data:
            raise serializers.ValidationError(
                {"items_data": "At least one item is required to create an order"}
            )

        return attrs

    def _calculate_item_total(self, item_data):
        """Calculate total amount for a single order item"""
        price = item_data.get("price")
        if not price:
            return Decimal("0.00")

        total = Decimal("0.00")

        # Calculate net quantity (quantity + advanced - return)
        net_ctn = (
            item_data.get("quantity_in_ctn", 0)
            + item_data.get("advanced_in_ctn", 0)
            - item_data.get("return_in_ctn", 0)
        )
        net_pcs = (
            item_data.get("quantity_in_pcs", 0)
            + item_data.get("advanced_in_pcs", 0)
            - item_data.get("return_in_pcs", 0)
        )

        # Calculate amount for cartons (handles both positive and negative net quantities)
        if price.ctn_price and net_ctn != 0:
            total += Decimal(str(net_ctn)) * price.ctn_price

        # Calculate amount for pieces (handles both positive and negative net quantities)
        if price.piece_price and net_pcs != 0:
            total += Decimal(str(net_pcs)) * price.piece_price

        return total

    def create(self, validated_data):
        """Create order with items - auto-calculate total_amount from items"""
        items_data = validated_data.pop("items_data", []) or []

        # Create the order
        order = OrderDelivery.objects.create(**validated_data)

        # Create order items and calculate total
        total_amount = Decimal("0.00")
        for item_data in items_data:
            # Calculate item total before creating
            item_total = self._calculate_item_total(item_data)
            total_amount += item_total
            OrderItem.objects.create(order=order, **item_data)

        # Update order total_amount
        order.total_amount = total_amount
        order.save()

        return order

    def update(self, instance, validated_data):
        """Update order and handle items - auto-calculate total_amount from items"""
        items_data = validated_data.pop("items_data", None)

        # If items_data is provided, recalculate total_amount from items
        if items_data is not None:
            # Delete existing items
            instance.items.all().delete()

            # Create new items and calculate total
            total_amount = Decimal("0.00")
            for item_data in items_data:
                # Calculate item total before creating
                item_total = self._calculate_item_total(item_data)
                total_amount += item_total
                OrderItem.objects.create(order=instance, **item_data)

            validated_data["total_amount"] = total_amount

        # Update order fields
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

