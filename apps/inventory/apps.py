from django.apps import AppConfig


class InventoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.inventory'

    def ready(self):
        """Initialize default stock types when app starts"""
        from .models import StockType
        
        default_stock_types = [
            'MAIN_STOCK',
            'REGULAR_STOCK',
            'DAMAGE_STOCK',
            'FREE_STOCK',
            'ADVANCE_STOCK',
        ]
        
        for stock_type_name in default_stock_types:
            StockType.objects.get_or_create(name=stock_type_name)

