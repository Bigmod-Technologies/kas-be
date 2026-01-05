from rest_framework import serializers
from decimal import Decimal
from apps.sales.models import SalesCollection, CollectionItem
from apps.product.serializers import ProductSerializer, ProductPriceSerializer
from apps.user.serializers.staff import UserSerializer
from apps.crm.serializers.customer import CustomerSerializer


class CollectionItemSerializer(serializers.ModelSerializer):
    """Serializer for CollectionItem (nested in SalesCollection)"""

    product_name = serializers.CharField(read_only=True, source="product.name")
    product_sku = serializers.CharField(read_only=True, source="product.sku")
    product_details = ProductSerializer(read_only=True, source="product")
    price_details = ProductPriceSerializer(read_only=True, source="price")
    total_order_amount = serializers.SerializerMethodField()
    total_damage_amount = serializers.SerializerMethodField()
    total_free_amount = serializers.SerializerMethodField()

    class Meta:
        model = CollectionItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_sku",
            "product_details",
            "price",
            "price_details",
            "order_cnt_qtn",
            "order_pcs_qtn",
            "damage_cnt_qtn",
            "damage_pcs_qtn",
            "free_cnt_qtn",
            "free_pcs_qtn",
            "total_order_amount",
            "total_damage_amount",
            "total_free_amount",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "product_name",
            "product_sku",
            "product_details",
            "price_details",
            "total_order_amount",
            "total_damage_amount",
            "total_free_amount",
            "created_at",
            "updated_at",
        )

    def get_total_order_amount(self, obj):
        """Get total order amount"""
        return obj.total_order_amount

    def get_total_damage_amount(self, obj):
        """Get total damage amount"""
        return obj.total_damage_amount

    def get_total_free_amount(self, obj):
        """Get total free amount"""
        return obj.total_free_amount


class CollectionItemWriteSerializer(serializers.ModelSerializer):
    """Serializer for writing CollectionItem data (nested in SalesCollection)"""

    class Meta:
        model = CollectionItem
        fields = [
            "product",
            "price",
            "order_cnt_qtn",
            "order_pcs_qtn",
            "damage_cnt_qtn",
            "damage_pcs_qtn",
            "free_cnt_qtn",
            "free_pcs_qtn",
        ]


class SalesCollectionSerializer(serializers.ModelSerializer):
    """Serializer for SalesCollection with nested items"""

    sales_by_details = UserSerializer(read_only=True, source="sales_by")
    customer_details = CustomerSerializer(read_only=True, source="customer")
    items = CollectionItemSerializer(many=True, read_only=True)
    items_data = CollectionItemWriteSerializer(
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
            "deduction_percentage",
            "collection_amount",
            "collection_by_personal_loan",
            "due_amount",
            "items",
            "items_data",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "sales_id",
            "sales_by_details",
            "customer_details",
            "total_sale",
            "commission_in_percentage",
            "special_discount_in_percentage",
            "deduction_percentage",
            "due_amount",
            "items",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):
        """Validate sales collection and items_data"""
        items_data = attrs.get("items_data", []) or []

        # Validate that items_data is provided for create
        if not self.instance and not items_data:
            raise serializers.ValidationError(
                {
                    "items_data": "At least one item is required to create a sales collection"
                }
            )

        return attrs

    def _calculate_item_order_amount(self, item_data, sales_collection=None):
        """Calculate net order amount for a single collection item (order - damage - free)"""
        price = item_data.get("price")
        if not price:
            return Decimal("0.00")

        total = Decimal("0.00")

        # Calculate order amount
        order_cnt_qtn = item_data.get("order_cnt_qtn", 0) or 0
        order_pcs_qtn = item_data.get("order_pcs_qtn", 0) or 0

        if price.ctn_price is not None and order_cnt_qtn:
            total += Decimal(str(price.ctn_price)) * Decimal(str(order_cnt_qtn))
        if price.piece_price is not None and order_pcs_qtn:
            total += Decimal(str(price.piece_price)) * Decimal(str(order_pcs_qtn))

        # Subtract damage amount
        damage_cnt_qtn = item_data.get("damage_cnt_qtn", 0) or 0
        damage_pcs_qtn = item_data.get("damage_pcs_qtn", 0) or 0

        damage_base = Decimal("0.00")
        if price.ctn_price is not None and damage_cnt_qtn:
            damage_base += Decimal(str(price.ctn_price)) * Decimal(str(damage_cnt_qtn))
        if price.piece_price is not None and damage_pcs_qtn:
            damage_base += Decimal(str(price.piece_price)) * Decimal(str(damage_pcs_qtn))

        # Apply deduction percentage to damage
        if sales_collection and sales_collection.deduction_percentage:
            deduction_rate = Decimal(str(sales_collection.deduction_percentage)) / Decimal(
                "100.00"
            )
            damage_amount = damage_base * (Decimal("1.00") - deduction_rate)
        else:
            damage_amount = damage_base

        total -= damage_amount

        # Subtract free amount
        free_cnt_qtn = item_data.get("free_cnt_qtn", 0) or 0
        free_pcs_qtn = item_data.get("free_pcs_qtn", 0) or 0

        free_amount = Decimal("0.00")
        if price.ctn_price is not None and free_cnt_qtn:
            free_amount += Decimal(str(price.ctn_price)) * Decimal(str(free_cnt_qtn))
        if price.piece_price is not None and free_pcs_qtn:
            free_amount += Decimal(str(price.piece_price)) * Decimal(str(free_pcs_qtn))

        total -= free_amount

        return total

    def create(self, validated_data):
        """Create sales collection with items - auto-calculate all fields"""
        items_data = validated_data.pop("items_data", []) or []
        customer = validated_data.get("customer")
        collection_amount = validated_data.get("collection_amount", Decimal("0.00"))
        collection_by_personal_loan = validated_data.get(
            "collection_by_personal_loan", Decimal("0.00")
        )

        # Auto-calculate commission and special discount from customer
        commission_in_percentage = Decimal("0.00")
        special_discount_in_percentage = Decimal("0.00")

        if customer:
            commission_in_percentage = customer.order_discount_in_persentage or Decimal(
                "0.00"
            )
            if customer.have_special_discount:
                special_discount_in_percentage = (
                    customer.special_discount_in_persentage or Decimal("0.00")
                )

        # Set default deduction percentage
        deduction_percentage = Decimal("10.00")

        # Create the sales collection
        sales_collection = SalesCollection.objects.create(
            **validated_data,
            commission_in_percentage=commission_in_percentage,
            special_discount_in_percentage=special_discount_in_percentage,
            deduction_percentage=deduction_percentage,
        )

        # Create collection items and calculate total sale
        total_sale = Decimal("0.00")
        for item_data in items_data:
            # Calculate item order amount before creating (order - damage - free)
            item_order_amount = self._calculate_item_order_amount(
                item_data, sales_collection
            )
            total_sale += item_order_amount
            CollectionItem.objects.create(sales=sales_collection, **item_data)

        # Calculate due amount
        due_amount = total_sale - collection_amount - collection_by_personal_loan

        # Update sales collection with calculated values
        sales_collection.total_sale = total_sale
        sales_collection.due_amount = due_amount
        sales_collection.save()

        return sales_collection

    def update(self, instance, validated_data):
        """Update sales collection and handle items - auto-calculate all fields"""
        items_data = validated_data.pop("items_data", None)
        customer = validated_data.get("customer", instance.customer)
        collection_amount = validated_data.get(
            "collection_amount", instance.collection_amount
        )
        collection_by_personal_loan = validated_data.get(
            "collection_by_personal_loan", instance.collection_by_personal_loan
        )

        # If items_data is provided, recalculate total_sale from items
        if items_data is not None:
            # Delete existing items
            instance.items.all().delete()

            # Create new items and calculate total
            total_sale = Decimal("0.00")
            for item_data in items_data:
                # Calculate item order amount before creating (order - damage - free)
                item_order_amount = self._calculate_item_order_amount(
                    item_data, instance
                )
                total_sale += item_order_amount
                CollectionItem.objects.create(sales=instance, **item_data)

            validated_data["total_sale"] = total_sale

        # Auto-update commission and special discount if customer changed
        if "customer" in validated_data and customer:
            validated_data["commission_in_percentage"] = (
                customer.order_discount_in_persentage or Decimal("0.00")
            )
            if customer.have_special_discount:
                validated_data["special_discount_in_percentage"] = (
                    customer.special_discount_in_persentage or Decimal("0.00")
                )
            else:
                validated_data["special_discount_in_percentage"] = Decimal("0.00")

        # Calculate due amount
        total_sale = validated_data.get("total_sale", instance.total_sale)
        due_amount = total_sale - collection_amount - collection_by_personal_loan
        validated_data["due_amount"] = due_amount

        # Update sales collection fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance
