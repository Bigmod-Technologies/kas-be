from rest_framework import serializers
from apps.product.models import Brand, Product, ProductPrice, PriceFor
from apps.product.utils import generate_sku


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = "__all__"


class ProductPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPrice
        fields = [
            "id",
            "price_for",
            "ctn_size",
            "ctn_price",
            "piece_price",
            "offer_price",
            "is_latest",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "created_at", "updated_at")


class ProductPriceWriteSerializer(serializers.ModelSerializer):
    """Serializer for writing price data (nested in Product)"""

    class Meta:
        model = ProductPrice
        fields = [
            "price_for",
            "ctn_size",
            "ctn_price",
            "piece_price",
            "offer_price",
        ]


class ProductSerializer(serializers.ModelSerializer):
    brand_details = BrandSerializer(read_only=True, source="brand")
    prices = ProductPriceSerializer(many=True, read_only=True)
    price = ProductPriceWriteSerializer(
        required=True, allow_null=True, source="latest_product_price"
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "brand",
            "brand_details",
            "have_offer",
            "status",
            "sku",
            "buy_qty",
            "free_qty",
            "price",
            "prices",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "brand_details", "prices", "created_at", "updated_at")

    def create(self, validated_data):
        """Create product and automatically create associated price if provided"""
        price_data = validated_data.pop("latest_product_price", None)

        # Create the product
        product = Product.objects.create(**validated_data)

        # Automatically create price if provided
        if price_data:
            # Ensure is_latest is True for new price
            price_data.setdefault("is_latest", True)
            ProductPrice.objects.create(product=product, **price_data)

        return product

    def update(self, instance, validated_data):
        """Update product and handle price logic according to business rules"""
        price_data = validated_data.pop("latest_product_price", None)

        # Update product fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        # Handle price update logic
        if price_data:
            # Check if price with same price_for already exists
            existing_price = ProductPrice.objects.filter(
                product=instance,
                price_for=PriceFor.PRODUCT,
                ctn_size=price_data.get("ctn_size"),
                piece_price=price_data.get("piece_price"),
                offer_price=price_data.get("offer_price"),
            ).first()

            if existing_price:
                existing_price.is_latest = True
                existing_price.save()
            else:
                # Price doesn't exist, create new one
                price_data.setdefault("is_latest", True)
                ProductPrice.objects.create(product=instance, **price_data)

        return instance


class SkuGenerateSerializer(serializers.Serializer):
    """
    Serializer for generating unique SKU numbers.
    Uses the generate_sku utility function for SKU generation logic.
    """
    sku = serializers.CharField(read_only=True)

    def to_representation(self, instance):
        """
        Override to generate and return the SKU using the utility function.
        """
        sku = generate_sku()
        return {"sku": sku}
