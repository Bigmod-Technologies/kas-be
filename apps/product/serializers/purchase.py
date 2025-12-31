from rest_framework import serializers
from apps.product.models import Purchase, PurchaseItem, PurchaseStatus
from apps.product.serializers import SupplierSerializer
from apps.product.utils import generate_voucher_number


class PurchaseItemSerializer(serializers.ModelSerializer):
    """Serializer for PurchaseItem (nested in Purchase)"""

    product_name = serializers.CharField(read_only=True, source="product.name")
    product_sku = serializers.CharField(read_only=True, source="product.sku")

    class Meta:
        model = PurchaseItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_sku",
            "quantity",
            "unit_price",
            "total_price",
            "unit",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "product_name",
            "product_sku",
            "total_price",
            "created_at",
            "updated_at",
        )


class PurchaseItemWriteSerializer(serializers.ModelSerializer):
    """Serializer for writing PurchaseItem data (nested in Purchase)"""

    class Meta:
        model = PurchaseItem
        fields = [
            "product",
            "quantity",
            "unit_price",
            "total_price",
            "unit",
        ]

    def validate(self, attrs):
        """Validate that total_price matches quantity * unit_price if provided"""
        total_price = attrs.get("total_price")
        quantity = attrs.get("quantity")
        unit_price = attrs.get("unit_price")

        if total_price and quantity and unit_price:
            calculated_total = quantity * unit_price
            if total_price != calculated_total:
                raise serializers.ValidationError(
                    {
                        "total_price": f"Total price should be {calculated_total} (quantity * unit_price)"
                    }
                )
        return attrs


class PurchaseSerializer(serializers.ModelSerializer):
    """Serializer for Purchase with nested items"""

    supplier_details = SupplierSerializer(read_only=True, source="supplier")
    items = PurchaseItemSerializer(many=True, read_only=True)
    items_data = PurchaseItemWriteSerializer(
        many=True, write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Purchase
        fields = [
            "id",
            "supplier",
            "supplier_details",
            "purchase_date",
            "total_amount",
            "paid_amount",
            "due_amount",
            "status",
            "note",
            "voucher_number",
            "items",
            "items_data",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "supplier_details",
            "items",
            "total_amount",
            "due_amount",
            "created_at",
            "updated_at",
        )
        extra_kwargs = {
            "paid_amount": {"required": False, "allow_null": True},
        }

    def validate(self, attrs):
        """Validate purchase amounts and items_data"""
        items_data = attrs.get("items_data", []) or []
        
        # Validate that items_data is provided for create
        if not self.instance and not items_data:
            raise serializers.ValidationError(
                {"items_data": "At least one item is required to create a purchase"}
            )

        return attrs

    def create(self, validated_data):
        """Create purchase with items - auto-calculate amounts from items"""
        items_data = validated_data.pop("items_data", []) or []

        # Calculate total_price for each item first
        for item_data in items_data:
            if not item_data.get("total_price"):
                item_data["total_price"] = item_data.get("quantity", 0) * item_data.get(
                    "unit_price", 0
                )

        # Calculate total_amount from sum of all items
        total_amount = sum(
            item.get("total_price", 0) for item in items_data
        )
        validated_data["total_amount"] = total_amount

        # Set paid_amount to 0 if not provided
        paid_amount = validated_data.get("paid_amount") or 0
        validated_data["paid_amount"] = paid_amount

        # Calculate due_amount automatically
        validated_data["due_amount"] = total_amount - paid_amount

        # Update status based on amounts
        if paid_amount == 0:
            validated_data["status"] = PurchaseStatus.PENDING
        elif paid_amount >= total_amount:
            validated_data["status"] = PurchaseStatus.PAID
        else:
            validated_data["status"] = PurchaseStatus.DUE

        # Create the purchase
        purchase = Purchase.objects.create(**validated_data)

        # Create purchase items
        for item_data in items_data:
            PurchaseItem.objects.create(purchase=purchase, **item_data)

        return purchase

    def update(self, instance, validated_data):
        """Update purchase and handle items - auto-calculate amounts from items"""
        items_data = validated_data.pop("items_data", None)

        # If items_data is provided, recalculate total_amount from items
        if items_data is not None:
            # Calculate total_price for each item first
            for item_data in items_data:
                if not item_data.get("total_price"):
                    item_data["total_price"] = item_data.get(
                        "quantity", 0
                    ) * item_data.get("unit_price", 0)

            # Calculate total_amount from sum of all items
            total_amount = sum(
                item.get("total_price", 0) for item in items_data
            )
            validated_data["total_amount"] = total_amount

        # Get paid_amount (use existing if not provided)
        paid_amount = validated_data.get("paid_amount")
        if paid_amount is None:
            paid_amount = instance.paid_amount
        else:
            validated_data["paid_amount"] = paid_amount

        # Get total_amount (use existing if not recalculated)
        total_amount = validated_data.get("total_amount", instance.total_amount)

        # Calculate due_amount automatically
        validated_data["due_amount"] = total_amount - paid_amount

        # Update status based on amounts
        if paid_amount == 0:
            validated_data["status"] = PurchaseStatus.PENDING
        elif paid_amount >= total_amount:
            validated_data["status"] = PurchaseStatus.PAID
        else:
            validated_data["status"] = PurchaseStatus.DUE

        # Update purchase fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # Handle items update
        if items_data is not None:
            # Delete existing items
            instance.items.all().delete()

            # Create new items
            for item_data in items_data:
                PurchaseItem.objects.create(purchase=instance, **item_data)

        return instance


class VoucherNumberGenerateSerializer(serializers.Serializer):
    """
    Serializer for generating unique voucher numbers.
    Uses the generate_voucher_number utility function for voucher number generation logic.
    """
    voucher_number = serializers.CharField(read_only=True)

    def to_representation(self, instance):
        """
        Override to generate and return the voucher number using the utility function.
        """
        voucher_number = generate_voucher_number()
        return {"voucher_number": voucher_number}
