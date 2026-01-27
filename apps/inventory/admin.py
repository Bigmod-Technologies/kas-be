from django.contrib import admin
from .models import StockType, StockTransaction


@admin.register(StockType)
class StockTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'updated_at']
    search_fields = ['name']
    list_filter = ['created_at', 'updated_at']
    ordering = ['name']


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'product',
        'product_price',
        'stock_type',
        'transaction_type',
        'ctn_quantity',
        'piece_quantity',
        'ctn_price',
        'piece_price',
        'total_price',
        'order_item',
        'have_transfer',
        'transfer_from',
        'transfer_to',
        'batch_number',
        'created_at'
    ]
    list_filter = [
        'transaction_type',
        'have_transfer',
        'stock_type',
        'created_at'
    ]
    search_fields = [
        'product__name',
        'stock_type__name',
        'note',
        'batch_number',
        'order_item__order__order_number'
    ]
    readonly_fields = ['total_price', 'created_at', 'updated_at']
    fieldsets = (
        ('Transaction Details', {
            'fields': ('stock_type', 'product', 'product_price', 'transaction_type', 'ctn_quantity', 'piece_quantity', 'ctn_price', 'piece_price', 'total_price')
        }),
        ('Order Information', {
            'fields': ('order_item',),
            'classes': ('collapse',)
        }),
        ('Transfer Information', {
            'fields': ('have_transfer', 'transfer_from', 'transfer_to'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('note', 'batch_number', 'created_at', 'updated_at')
        }),
    )
    ordering = ['-created_at']
