from django.contrib import admin

from .models import StockTransaction, StockType


@admin.register(StockType)
class StockTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at", "updated_at"]
    search_fields = ["name"]
    list_filter = ["created_at", "updated_at"]
    ordering = ["name"]


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = [
        "product",
        "product_price",
        "stock_type",
        "transaction_type",
        "ctn_quantity",
        "piece_quantity",
        "ctn_price",
        "piece_price",
        "total_price",
        "source_item",
        "have_transfer",
        "transfer_from",
        "transfer_to",
        "batch_number",
        "created_at",
    ]
    list_filter = ["transaction_type", "have_transfer", "stock_type", "created_at"]
    list_select_related = [
        "product",
        "product_price",
        "stock_type",
        "order_item",
        "order_item__order",
        "damage_order_item",
        "free_offer_item",
    ]
    search_fields = [
        "product__name",
        "product__sku",
        "stock_type__name",
        "note",
        "batch_number",
        "order_item__order__order_number",
    ]
    readonly_fields = ["total_price", "created_at", "updated_at"]
    raw_id_fields = [
        "product",
        "product_price",
        "stock_type",
        "order_item",
        "damage_order_item",
        "free_offer_item",
    ]
    fieldsets = (
        (
            "Transaction Details",
            {
                "fields": (
                    "stock_type",
                    "product",
                    "product_price",
                    "transaction_type",
                    "ctn_quantity",
                    "piece_quantity",
                    "ctn_price",
                    "piece_price",
                    "total_price",
                ),
            },
        ),
        (
            "Source",
            {
                "fields": ("order_item", "damage_order_item", "free_offer_item"),
                "classes": ("collapse",),
            },
        ),
        (
            "Transfer",
            {
                "fields": ("have_transfer", "transfer_from", "transfer_to"),
                "classes": ("collapse",),
            },
        ),
        (
            "Additional",
            {"fields": ("note", "batch_number", "created_at", "updated_at")},
        ),
    )
    ordering = ["-created_at"]

    def source_item(self, obj):
        """Show which order item type this transaction came from."""
        if obj.order_item_id:
            return f"Order #{obj.order_item.order.order_number}"
        if obj.damage_order_item_id:
            return "Damage"
        if obj.free_offer_item_id:
            return "Free Offer"
        return "-"

    source_item.short_description = "Source"
