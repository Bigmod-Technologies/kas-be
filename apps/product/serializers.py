from rest_framework import serializers
from .models import Brand, Product


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    brand_details = BrandSerializer(read_only=True, source="brand")

    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = ("brand_details",)
