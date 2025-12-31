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
        'price',
        'have_transfer',
        'transfer_from',
        'transfer_to',
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
        'note'
    ]
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Transaction Details', {
            'fields': ('stock_type', 'product', 'price', 'transaction_type', 'ctn_quantity', 'piece_quantity')
        }),
        ('Transfer Information', {
            'fields': ('have_transfer', 'transfer_from', 'transfer_to'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('note', 'created_at', 'updated_at')
        }),
    )
    ordering = ['-created_at']
