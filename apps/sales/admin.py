from django.contrib import admin
from django.utils.html import format_html
from apps.sales.models import (
    OrderDelivery, 
    OrderItem, 
    DamageOrderItem, 
    FreeOfferItem,
    SalesCollection, 
    DamageItem, 
    FreeItem
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


class DamageItemInline(admin.TabularInline):
    """Inline admin for DamageItem in SalesCollection admin"""
    
    model = DamageItem
    extra = 0
    fields = [
        "product",
        "price",
        ("cnt_qtn", "pcs_qtn"),
        "deduction_percentage",
    ]
    raw_id_fields = ["product", "price"]
    verbose_name = "Damage Item"
    verbose_name_plural = "Damage Items"


class FreeItemInline(admin.TabularInline):
    """Inline admin for FreeItem in SalesCollection admin"""
    
    model = FreeItem
    extra = 0
    fields = [
        "product",
        "price",
        ("cnt_qtn", "pcs_qtn"),
    ]
    raw_id_fields = ["product", "price"]
    verbose_name = "Free Item"
    verbose_name_plural = "Free Items"


@admin.register(SalesCollection)
class SalesCollectionAdmin(admin.ModelAdmin):
    """Admin interface for SalesCollection model"""
    
    list_display = [
        "sales_id",
        "sales_date",
        "sales_by",
        "customer",
        "total_sale",
        "collection_amount",
        "created_at",
    ]
    list_display_links = ["sales_id"]
    search_fields = [
        "sales_id",
        "sales_by__username",
        "sales_by__email",
        "customer__name",
        "customer__shop_name",
    ]
    list_filter = [
        "sales_date",
        "created_at",
        "sales_by",
        "customer",
    ]
    readonly_fields = [
        "id",
        "sales_id",
        "created_at",
        "updated_at",
    ]
    raw_id_fields = ["sales_by", "customer"]
    inlines = [DamageItemInline, FreeItemInline]
    date_hierarchy = "sales_date"
    ordering = ["-sales_date", "-sales_id"]
    
    fieldsets = (
        ("Sales Information", {
            "fields": (
                "id",
                "sales_id",
                "sales_date",
            )
        }),
        ("Relations", {
            "fields": (
                "sales_by",
                "customer",
            )
        }),
        ("Financial", {
            "fields": (
                "total_sale",
                "commission_in_percentage",
                "special_discount_in_percentage",
                "collection_amount",
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
    

@admin.register(DamageItem)
class DamageItemAdmin(admin.ModelAdmin):
    """Admin interface for DamageItem model"""
    
    list_display = [
        "sales",
        "product",
        "quantity_display",
        "created_at",
    ]
    list_display_links = ["sales", "product"]
    search_fields = [
        "sales__sales_id",
        "product__name",
        "product__sku",
    ]
    list_filter = [
        "sales__sales_date",
        "created_at",
        "sales__customer",
    ]
    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
    ]
    raw_id_fields = ["sales", "product", "price"]
    ordering = ["-created_at", "-sales"]
    
    fieldsets = (
        ("Sales Collection Information", {
            "fields": (
                "id",
                "sales",
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
                ("cnt_qtn", "pcs_qtn"),
            )
        }),
        ("Deduction", {
            "fields": (
                "deduction_percentage",
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
    
    def quantity_display(self, obj):
        """Display quantity in a formatted way"""
        if obj.cnt_qtn or obj.pcs_qtn:
            return format_html(
                '<span style="color: red;">CTN: <strong>{}</strong> | PCS: <strong>{}</strong></span>',
                obj.cnt_qtn,
                obj.pcs_qtn
            )
        return "-"
    quantity_display.short_description = "Quantity"


@admin.register(FreeItem)
class FreeItemAdmin(admin.ModelAdmin):
    """Admin interface for FreeItem model"""
    
    list_display = [
        "sales",
        "product",
        "quantity_display",
        "created_at",
    ]
    list_display_links = ["sales", "product"]
    search_fields = [
        "sales__sales_id",
        "product__name",
        "product__sku",
    ]
    list_filter = [
        "sales__sales_date",
        "created_at",
        "sales__customer",
    ]
    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
    ]
    raw_id_fields = ["sales", "product", "price"]
    ordering = ["-created_at", "-sales"]
    
    fieldsets = (
        ("Sales Collection Information", {
            "fields": (
                "id",
                "sales",
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
                ("cnt_qtn", "pcs_qtn"),
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
    
    def quantity_display(self, obj):
        """Display quantity in a formatted way"""
        if obj.cnt_qtn or obj.pcs_qtn:
            return format_html(
                '<span style="color: green;">CTN: <strong>{}</strong> | PCS: <strong>{}</strong></span>',
                obj.cnt_qtn,
                obj.pcs_qtn
            )
        return "-"
    quantity_display.short_description = "Quantity"

