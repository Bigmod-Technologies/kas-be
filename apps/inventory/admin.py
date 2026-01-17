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
        'stock_type',
        'transaction_type',
        'ctn_quantity',
        'piece_quantity',
        'ctn_price',
        'piece_price',
        'total_price',
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
        'batch_number'
    ]
    readonly_fields = ['total_price', 'created_at', 'updated_at']
    fieldsets = (
        ('Transaction Details', {
            'fields': ('stock_type', 'product', 'transaction_type', 'ctn_quantity', 'piece_quantity', 'ctn_price', 'piece_price', 'total_price')
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
