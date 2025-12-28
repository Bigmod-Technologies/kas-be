from django.contrib import admin
from apps.product.models import Brand, Product


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
    list_display = ["name", "brand", "ctn_price", "offer_price", "status"]
    search_fields = ["name", "sku"]
    list_filter = ["status", "brand", "have_offer"]
