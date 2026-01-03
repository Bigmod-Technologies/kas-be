from django.contrib import admin
from django.utils.html import format_html
from apps.sales.models import OrderDelivery, OrderItem


class OrderItemInline(admin.TabularInline):
    """Inline admin for OrderItem in OrderDelivery admin"""
    
    model = OrderItem
    extra = 0
    fields = [
        "product",
        "price",
        "shift",
        ("quantity_in_ctn", "quantity_in_pcs"),
        ("advanced_in_ctn", "advanced_in_pcs"),
        ("damaged_in_ctn", "damaged_in_pcs"),
        "total_amount",
    ]
    readonly_fields = ["total_amount"]
    raw_id_fields = ["product", "price"]
    verbose_name = "Order Item"
    verbose_name_plural = "Order Items"


@admin.register(OrderDelivery)
class OrderDeliveryAdmin(admin.ModelAdmin):
    """Admin interface for OrderDelivery model"""
    
    list_display = [
        "order_number",
        "order_date",
        "order_by",
        "customer",
        "total_amount",
        "items_count",
        "created_at",
    ]
    list_display_links = ["order_number"]
    search_fields = [
        "order_number",
        "order_by__username",
        "order_by__email",
        "customer__name",
        "customer__shop_name",
    ]
    list_filter = [
        "order_date",
        "created_at",
        "order_by",
        "customer",
    ]
    readonly_fields = [
        "id",
        "order_number",
        "created_at",
        "updated_at",
    ]
    raw_id_fields = ["order_by", "customer"]
    inlines = [OrderItemInline]
    date_hierarchy = "order_date"
    ordering = ["-order_date", "-order_number"]
    
    fieldsets = (
        ("Order Information", {
            "fields": (
                "id",
                "order_number",
                "order_date",
            )
        }),
        ("Relations", {
            "fields": (
                "order_by",
                "customer",
            )
        }),
        ("Financial", {
            "fields": (
                "total_amount",
            )
        }),
        ("Timestamps", {
            "fields": (
                "created_at",
                "updated_at",
            ),
            "classes": ("collapse",)
        }),
    )
    
    def items_count(self, obj):
        """Display the count of items in the order"""
        count = obj.items.count()
        return format_html(
            '<span style="font-weight: bold;">{}</span>',
            count
        )
    items_count.short_description = "Items"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin interface for OrderItem model"""
    
    list_display = [
        "order",
        "product",
        "shift",
        "quantity_display",
        "advanced_display",
        "damaged_display",
        "total_amount",
        "created_at",
    ]
    list_display_links = ["order", "product"]
    search_fields = [
        "order__order_number",
        "product__name",
        "product__sku",
    ]
    list_filter = [
        "shift",
        "order__order_date",
        "created_at",
        "order__customer",
    ]
    readonly_fields = [
        "id",
        "total_amount",
        "created_at",
        "updated_at",
    ]
    raw_id_fields = ["order", "product", "price"]
    ordering = ["-created_at", "-order"]
    
    fieldsets = (
        ("Order Information", {
            "fields": (
                "id",
                "order",
            )
        }),
        ("Product & Price", {
            "fields": (
                "product",
                "price",
                "shift",
            )
        }),
        ("Quantities", {
            "fields": (
                ("quantity_in_ctn", "quantity_in_pcs"),
                ("advanced_in_ctn", "advanced_in_pcs"),
                ("damaged_in_ctn", "damaged_in_pcs"),
            )
        }),
        ("Financial", {
            "fields": ("total_amount",)
        }),
        ("Timestamps", {
            "fields": (
                "created_at",
                "updated_at",
            ),
            "classes": ("collapse",)
        }),
    )
    
    def quantity_display(self, obj):
        """Display quantity in a formatted way"""
        if obj.quantity_in_ctn or obj.quantity_in_pcs:
            return format_html(
                '<span>CTN: <strong>{}</strong> | PCS: <strong>{}</strong></span>',
                obj.quantity_in_ctn,
                obj.quantity_in_pcs
            )
        return "-"
    quantity_display.short_description = "Quantity"
    
    def advanced_display(self, obj):
        """Display advanced quantity in a formatted way"""
        if obj.advanced_in_ctn or obj.advanced_in_pcs:
            return format_html(
                '<span style="color: green;">CTN: <strong>{}</strong> | PCS: <strong>{}</strong></span>',
                obj.advanced_in_ctn,
                obj.advanced_in_pcs
            )
        return "-"
    advanced_display.short_description = "Advanced"
    
    def damaged_display(self, obj):
        """Display damaged quantity in a formatted way"""
        if obj.damaged_in_ctn or obj.damaged_in_pcs:
            return format_html(
                '<span style="color: red;">CTN: <strong>{}</strong> | PCS: <strong>{}</strong></span>',
                obj.damaged_in_ctn,
                obj.damaged_in_pcs
            )
        return "-"
    damaged_display.short_description = "Damaged"
