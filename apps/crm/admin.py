from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = [
        'customer_id',
        'name',
        'shop_name',
        'shop_name_en',
        'contact_number',
        'area',
        'fridge_type',
        'opening_balance',
        'due_limit',
        'order_discount_in_persentage',
        'have_special_discount',
        'special_discount_in_persentage',
        'created_at'
    ]
    list_filter = [
        'area',
        'fridge_type',
        'have_special_discount',
        'created_at',
        'updated_at'
    ]
    search_fields = [
        'customer_id',
        'name',
        'shop_name',
        'contact_number',
        'address'
    ]
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer_id', 'name', 'shop_name', 'contact_number', 'address', 'fridge_type')
        }),
        ('Location', {
            'fields': ('area',)
        }),
        ('Financial Information', {
            'fields': ('opening_balance', 'due_limit', 'order_discount_in_persentage')
        }),
        ('Discount Information', {
            'fields': ('have_special_discount', 'special_discount_in_persentage')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ['name']
