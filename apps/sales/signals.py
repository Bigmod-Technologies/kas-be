from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.sales.models import OrderItem, DamageOrderItem, FreeOfferItem
from apps.inventory.models import StockTransaction, StockType, TransactionType


@receiver(post_save, sender=OrderItem)
def create_stock_transaction_on_order_item_created(sender, instance, created, **kwargs):
    """
    Signal handler to create a StockTransaction when an OrderItem is created.

    Case 1: Regular quantities and returns are OUT from Regular Stock
    - Regular quantity (quantity_in_ctn, quantity_in_pcs): OUT from Regular Stock
    - Return quantity (return_in_ctn, return_in_pcs): OUT from Regular Stock

    Case 2: Advanced quantities are IN to Advance Stock
    - Advanced quantity (advanced_in_ctn, advanced_in_pcs): IN to Advance Stock
    """
    if created:
        # Get stock types
        regular_stock_type = StockType.objects.get(name="Regular Stock")
        advance_stock_type = StockType.objects.get(name="Advance Stock")

        # Case 1: Calculate net quantity (quantity - return) for Regular Stock OUT
        # This is the actual stock that goes out from Regular Stock
        net_ctn_quantity = instance.quantity_in_ctn - instance.return_in_ctn
        net_pcs_quantity = instance.quantity_in_pcs - instance.return_in_pcs

        # Only create transaction if net quantity is positive
        if net_ctn_quantity > 0 or net_pcs_quantity > 0:
            StockTransaction.objects.create(
                stock_type=regular_stock_type,
                product=instance.product,
                product_price=instance.price,
                transaction_type=TransactionType.OUT.value,
                ctn_quantity=net_ctn_quantity,
                piece_quantity=net_pcs_quantity,
                order_item=instance,
                note=f"Net quantity (quantity - return) for order {instance.order.order_number}",
            )

        # Case 2: Handle advanced quantities (advanced_in_ctn and advanced_in_pcs)
        # Advanced quantities are IN to Advance Stock
        advanced_ctn_quantity = instance.advanced_in_ctn
        advanced_pcs_quantity = instance.advanced_in_pcs

        if advanced_ctn_quantity > 0 or advanced_pcs_quantity > 0:
            StockTransaction.objects.create(
                stock_type=advance_stock_type,
                product=instance.product,
                product_price=instance.price,
                transaction_type=TransactionType.IN.value,
                ctn_quantity=advanced_ctn_quantity,
                piece_quantity=advanced_pcs_quantity,
                order_item=instance,
                note=f"Advanced quantity for order {instance.order.order_number}",
            )


@receiver(post_save, sender=DamageOrderItem)
def create_stock_transaction_on_damage_order_item_created(
    sender, instance, created, **kwargs
):
    """
    Signal handler to create a StockTransaction when a DamageOrderItem is created.

    Damaged items are OUT from Damage Stock (stock going out due to damage).
    """
    if created:
        # Get stock type
        damage_stock_type = StockType.objects.get(name="Damage Stock")

        # Handle damaged quantities (quantity_in_ctn and quantity_in_pcs)
        # These are OUT from Damage Stock
        ctn_quantity = instance.quantity_in_ctn
        pcs_quantity = instance.quantity_in_pcs

        if ctn_quantity > 0 or pcs_quantity > 0:
            StockTransaction.objects.create(
                stock_type=damage_stock_type,
                product=instance.product,
                product_price=instance.price,
                transaction_type=TransactionType.IN.value,
                ctn_quantity=ctn_quantity,
                piece_quantity=pcs_quantity,
                damage_order_item=instance,
                note=f"Damaged quantity for order {instance.order.order_number}"
                + (f" - {instance.damage_reason}" if instance.damage_reason else ""),
            )


@receiver(post_save, sender=FreeOfferItem)
def create_stock_transaction_on_free_offer_item_created(
    sender, instance, created, **kwargs
):
    """
    Signal handler to create a StockTransaction when a FreeOfferItem is created.

    Free offer items are OUT from Free Offer Stock (stock given away for free).
    """
    if created:
        # Get stock type
        free_offer_stock_type = StockType.objects.get(name="Free Stock")

        # Handle free offer quantities (quantity_in_ctn and quantity_in_pcs)
        # These are OUT from Free Offer Stock
        ctn_quantity = instance.quantity_in_ctn
        pcs_quantity = instance.quantity_in_pcs

        if ctn_quantity > 0 or pcs_quantity > 0:
            StockTransaction.objects.create(
                stock_type=free_offer_stock_type,
                product=instance.product,
                product_price=instance.price,
                transaction_type=TransactionType.OUT.value,
                ctn_quantity=ctn_quantity,
                piece_quantity=pcs_quantity,
                free_offer_item=instance,
                note=f"Free offer quantity for order {instance.order.order_number}",
            )
