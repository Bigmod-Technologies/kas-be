from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'shop_name',
        'contact_number',
        'zone',
        'opening_balance',
        'due_limit',
        'created_at'
    ]
    list_filter = [
        'zone',
        'created_at',
        'updated_at'
    ]
    search_fields = [
        'name',
        'shop_name',
        'contact_number',
        'address'
    ]
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Customer Information', {
            'fields': ('name', 'shop_name', 'contact_number', 'address')
        }),
        ('Financial Information', {
            'fields': ('opening_balance', 'due_limit')
        }),
        ('Location', {
            'fields': ('zone',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ['name']
