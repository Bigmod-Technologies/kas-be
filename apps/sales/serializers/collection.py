from rest_framework import serializers
from decimal import Decimal
from apps.sales.models import SalesCollection, DamageItem, FreeItem
from apps.product.serializers import ProductSerializer, ProductPriceSerializer
from apps.user.serializers.staff import UserSerializer
from apps.crm.serializers.customer import CustomerSerializer


class DamageItemSerializer(serializers.ModelSerializer):
    """Serializer for DamageItem (nested in SalesCollection)"""

    product_name = serializers.CharField(read_only=True, source="product.name")
    product_sku = serializers.CharField(read_only=True, source="product.sku")
    product_details = ProductSerializer(read_only=True, source="product")
    price_details = ProductPriceSerializer(read_only=True, source="price")

    class Meta:
        model = DamageItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_sku",
            "product_details",
            "price",
            "price_details",
            "cnt_qtn",
            "pcs_qtn",
            "deduction_percentage",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "product_name",
            "product_sku",
            "product_details",
            "price_details",
            "created_at",
            "updated_at",
        )


class DamageItemWriteSerializer(serializers.ModelSerializer):
    """Serializer for writing DamageItem data (nested in SalesCollection)"""

    class Meta:
        model = DamageItem
        fields = [
            "product",
            "price",
            "cnt_qtn",
            "pcs_qtn",
            "deduction_percentage",
        ]


class FreeItemSerializer(serializers.ModelSerializer):
    """Serializer for FreeItem (nested in SalesCollection)"""

    product_name = serializers.CharField(read_only=True, source="product.name")
    product_sku = serializers.CharField(read_only=True, source="product.sku")
    product_details = ProductSerializer(read_only=True, source="product")
    price_details = ProductPriceSerializer(read_only=True, source="price")

    class Meta:
        model = FreeItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_sku",
            "product_details",
            "price",
            "price_details",
            "cnt_qtn",
            "pcs_qtn",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "product_name",
            "product_sku",
            "product_details",
            "price_details",
            "created_at",
            "updated_at",
        )


class FreeItemWriteSerializer(serializers.ModelSerializer):
    """Serializer for writing FreeItem data (nested in SalesCollection)"""

    class Meta:
        model = FreeItem
        fields = [
            "product",
            "price",
            "cnt_qtn",
            "pcs_qtn",
        ]


class SalesCollectionSerializer(serializers.ModelSerializer):
    """Serializer for SalesCollection with nested damage and free items"""

    sales_by_details = UserSerializer(read_only=True, source="sales_by")
    customer_details = CustomerSerializer(read_only=True, source="customer")
    damage_items = DamageItemSerializer(many=True, read_only=True)
    damage_items_data = DamageItemWriteSerializer(
        many=True, write_only=True, required=False, allow_null=True
    )
    free_items = FreeItemSerializer(many=True, read_only=True)
    free_items_data = FreeItemWriteSerializer(
        many=True, write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = SalesCollection
        fields = [
            "id",
            "sales_id",
            "sales_date",
            "sales_by",
            "sales_by_details",
            "customer",
            "customer_details",
            "total_sale",
            "commission_in_percentage",
            "special_discount_in_percentage",
            "collection_amount",
            "damage_items",
            "damage_items_data",
            "free_items",
            "free_items_data",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "sales_id",
            "sales_by_details",
            "customer_details",
            "commission_in_percentage",
            "special_discount_in_percentage",
            "damage_items",
            "free_items",
            "created_at",
            "updated_at",
        )

    def create(self, validated_data):
        """Create sales collection with damage and free items"""
        damage_items_data = validated_data.pop("damage_items_data", []) or []
        free_items_data = validated_data.pop("free_items_data", []) or []

        # Create the sales collection
        sales_collection = SalesCollection.objects.create(**validated_data)

        # Create damage items
        for item_data in damage_items_data:
            DamageItem.objects.create(sales=sales_collection, **item_data)

        # Create free items
        for item_data in free_items_data:
            FreeItem.objects.create(sales=sales_collection, **item_data)

        return sales_collection

    def update(self, instance, validated_data):
        """Update sales collection and handle damage and free items"""
        damage_items_data = validated_data.pop("damage_items_data", None)
        free_items_data = validated_data.pop("free_items_data", None)

        # Update sales collection fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # If damage_items_data is provided, replace existing damage items
        if damage_items_data is not None:
            instance.damage_items.all().delete()
            for item_data in damage_items_data:
                DamageItem.objects.create(sales=instance, **item_data)

        # If free_items_data is provided, replace existing free items
        if free_items_data is not None:
            instance.free_items.all().delete()
            for item_data in free_items_data:
                FreeItem.objects.create(sales=instance, **item_data)

        return instance
