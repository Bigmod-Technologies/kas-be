from django.contrib import admin
from .models import Area, Zone, WorkingDay


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'zone',
        'route_number',
        'created_at',
        'updated_at'
    ]
    list_filter = [
        'zone',
        'created_at',
        'updated_at'
    ]
    search_fields = [
        'name',
        'route_number'
    ]
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['working_days']
    fieldsets = (
        ('Area Information', {
            'fields': ('name', 'zone', 'route_number')
        }),
        ('Working Days', {
            'fields': ('working_days',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ['name']


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'is_archive',
        'created_at',
        'updated_at'
    ]
    list_filter = [
        'is_archive',
        'created_at',
        'updated_at'
    ]
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']


@admin.register(WorkingDay)
class WorkingDayAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'created_at',
        'updated_at'
    ]
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
