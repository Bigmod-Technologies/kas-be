from django.contrib import admin
from apps.product.models import Brand, Product, ProductPrice, Supplier, Purchase, PurchaseItem


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


class ProductPriceInline(admin.TabularInline):
    model = ProductPrice
    extra = 0
    fields = ["price_for", "ctn_size", "ctn_price", "piece_price", "offer_price", "is_latest", "created_at"]
    readonly_fields = ["created_at"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "brand", "sku", "have_offer", "status", "created_at"]
    search_fields = ["name", "sku"]
    list_filter = ["status", "brand", "have_offer", "created_at"]
    readonly_fields = ["id", "created_at", "updated_at"]
    inlines = [ProductPriceInline]


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


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = [
        "brand_name",
        "status",
        "representative_name",
        "representative_contact_number",
        "opening_balance",
        "due_limit",
        "registration_number",
        "created_at",
    ]
    search_fields = ["brand_name", "representative_name", "registration_number"]
    list_filter = ["status", "created_at"]
    readonly_fields = ["id", "created_at", "updated_at"]


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 0
    fields = ["product", "quantity", "unit", "unit_price", "total_price", "created_at"]
    readonly_fields = ["total_price", "created_at"]
    raw_id_fields = ["product"]


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = [
        "voucher_number",
        "supplier",
        "purchase_date",
        "total_amount",
        "paid_amount",
        "due_amount",
        "status",
        "created_at",
    ]
    search_fields = ["voucher_number", "supplier__brand_name"]
    list_filter = ["status", "purchase_date", "created_at"]
    readonly_fields = ["id", "created_at", "updated_at"]
    raw_id_fields = ["supplier"]
    inlines = [PurchaseItemInline]
