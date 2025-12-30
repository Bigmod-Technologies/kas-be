from django.contrib import admin
from apps.product.models import Brand, Product, ProductPrice


# Register your models here.
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "status",
        "representative_name",
        "representative_contact_number",
    ]
    search_fields = ["name", "representative_name"]
    list_filter = ["status"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "brand", "sku", "have_offer", "status", "created_at"]
    search_fields = ["name", "sku"]
    list_filter = ["status", "brand", "have_offer", "created_at"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(ProductPrice)
class ProductPriceAdmin(admin.ModelAdmin):
    list_display = [
        "product",
        "price_for",
        "ctn_price",
        "piece_price",
        "offer_price",
        "is_latest",
        "created_at",
    ]
    search_fields = ["product__name", "product__sku"]
    list_filter = ["price_for", "is_latest", "created_at"]
    readonly_fields = ["id", "created_at", "updated_at"]
    raw_id_fields = ["product"]
