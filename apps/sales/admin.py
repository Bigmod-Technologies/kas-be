from django.contrib import admin
from django.utils.html import format_html
from apps.sales.models import (
    OrderDelivery,
    OrderItem,
    DamageOrderItem,
    FreeOfferItem,
    DueSell,
    DueCollection,
)


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
        ("return_in_ctn", "return_in_pcs"),
        "total_amount",
    ]
    readonly_fields = ["total_amount"]
    raw_id_fields = ["product", "price"]
    verbose_name = "Order Item"
    verbose_name_plural = "Order Items"


class DamageOrderItemInline(admin.TabularInline):
    """Inline admin for DamageOrderItem in OrderDelivery admin"""
    
    model = DamageOrderItem
    extra = 0
    fields = [
        "product",
        "price",
        ("quantity_in_ctn", "quantity_in_pcs"),
        "damage_reason",
        "total_amount",
    ]
    readonly_fields = ["total_amount"]
    raw_id_fields = ["product", "price"]
    verbose_name = "Damage Order Item"
    verbose_name_plural = "Damage Order Items"


class FreeOfferItemInline(admin.TabularInline):
    """Inline admin for FreeOfferItem in OrderDelivery admin"""
    
    model = FreeOfferItem
    extra = 0
    fields = [
        "product",
        "price",
        ("quantity_in_ctn", "quantity_in_pcs"),
        "total_amount",
    ]
    readonly_fields = ["total_amount"]
    raw_id_fields = ["product", "price"]
    verbose_name = "Free Offer Item"
    verbose_name_plural = "Free Offer Items"


@admin.register(OrderDelivery)
class OrderDeliveryAdmin(admin.ModelAdmin):
    """Admin interface for OrderDelivery model"""
    
    list_display = [
        "order_number",
        "order_date",
        "order_by",
        "cash_sell_amount",
        "priojon_offer",
        "items_count",
        "created_at",
    ]
    list_display_links = ["order_number"]
    search_fields = [
        "order_number",
        "order_by__username",
        "order_by__email",
        "narration",
    ]
    list_filter = [
        "order_date",
        "created_at",
        "order_by",
    ]
    readonly_fields = [
        "id",
        "order_number",
        "created_at",
        "updated_at",
    ]
    raw_id_fields = ["order_by"]
    inlines = [OrderItemInline, DamageOrderItemInline, FreeOfferItemInline]
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
            )
        }),
        ("Financial", {
            "fields": (
                "cash_sell_amount",
                "priojon_offer",
            )
        }),
        ("Additional Information", {
            "fields": (
                "narration",
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
        damage_count = obj.damage_items.count()
        free_offer_count = obj.free_offer_items.count()
        total = count + damage_count + free_offer_count
        return format_html(
            '<span style="font-weight: bold;">Total: {}</span><br>'
            '<span style="color: #666;">Items: {}, Damage: {}, Free: {}</span>',
            total, count, damage_count, free_offer_count
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
                ("return_in_ctn", "return_in_pcs"),
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
        if obj.return_in_ctn or obj.return_in_pcs:
            return format_html(
                '<span style="color: red;">CTN: <strong>{}</strong> | PCS: <strong>{}</strong></span>',
                obj.return_in_ctn,
                obj.return_in_pcs
            )
        return "-"
    damaged_display.short_description = "Damaged"


@admin.register(DamageOrderItem)
class DamageOrderItemAdmin(admin.ModelAdmin):
    """Admin interface for DamageOrderItem model"""
    
    list_display = [
        "order",
        "product",
        "quantity_display",
        "total_amount",
        "created_at",
    ]
    list_display_links = ["order", "product"]
    search_fields = [
        "order__order_number",
        "product__name",
        "product__sku",
        "damage_reason",
    ]
    list_filter = [
        "order__order_date",
        "created_at",
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
            )
        }),
        ("Quantities", {
            "fields": (
                ("quantity_in_ctn", "quantity_in_pcs"),
            )
        }),
        ("Damage Information", {
            "fields": (
                "damage_reason",
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
                '<span style="color: red;">CTN: <strong>{}</strong> | PCS: <strong>{}</strong></span>',
                obj.quantity_in_ctn,
                obj.quantity_in_pcs
            )
        return "-"
    quantity_display.short_description = "Quantity"


@admin.register(FreeOfferItem)
class FreeOfferItemAdmin(admin.ModelAdmin):
    """Admin interface for FreeOfferItem model"""
    
    list_display = [
        "order",
        "product",
        "quantity_display",
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
        "order__order_date",
        "created_at",
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
            )
        }),
        ("Quantities", {
            "fields": (
                ("quantity_in_ctn", "quantity_in_pcs"),
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
                '<span style="color: green;">CTN: <strong>{}</strong> | PCS: <strong>{}</strong></span>',
                obj.quantity_in_ctn,
                obj.quantity_in_pcs
            )
        return "-"
    quantity_display.short_description = "Quantity"


@admin.register(DueSell)
class DueSellAdmin(admin.ModelAdmin):
    """Admin interface for DueSell model."""

    list_display = [
        "order",
        "customer",
        "deliver_by",
        "sale_date",
        "amount",
        "created_at",
    ]
    list_filter = [
        "sale_date",
        "created_at",
        "deliver_by",
        "customer",
        "order",
    ]
    search_fields = [
        "customer__name",
        "customer__shop_name",
        "deliver_by__username",
    ]
    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
    ]
    raw_id_fields = [
        "order",
        "customer",
        "deliver_by",
    ]
    ordering = ["-sale_date", "-created_at"]


@admin.register(DueCollection)
class DueCollectionAdmin(admin.ModelAdmin):
    """Admin interface for DueCollection model."""

    list_display = [
        "customer",
        "collected_by",
        "collection_date",
        "amount",
        "created_at",
    ]
    list_filter = [
        "collection_date",
        "created_at",
        "collected_by",
        "customer",
    ]
    search_fields = [
        "customer__name",
        "customer__shop_name",
        "collected_by__username",
    ]
    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
    ]
    raw_id_fields = [
        "customer",
        "collected_by",
    ]
    ordering = ["-collection_date", "-created_at"]



