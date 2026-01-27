from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.sales.models import OrderItem
from apps.inventory.models import StockTransaction, StockType, TransactionType


@receiver(post_save, sender=OrderItem)
def create_stock_transaction_on_order_item_created(sender, instance, created, **kwargs):
    """
    Signal handler to create a StockTransaction when an OrderItem is created.
    Creates OUT transactions for regular and advanced quantities.
    Creates IN transactions for return quantities (stock coming back in).
    """
    if created:
        # Get stock types
        regular_stock_type = StockType.objects.get(name="Regular Stock")
        advance_stock_type = StockType.objects.get(name="Advance Stock")

        # Handle regular quantities (quantity_in_ctn and quantity_in_pcs)
        ctn_quantity = instance.quantity_in_ctn
        pcs_quantity = instance.quantity_in_pcs

        if ctn_quantity > 0 or pcs_quantity > 0:
            # Create transaction for regular quantities
            StockTransaction.objects.create(
                stock_type=regular_stock_type,
                product=instance.product,
                product_price=instance.price,
                transaction_type=TransactionType.OUT,
                ctn_quantity=ctn_quantity,
                piece_quantity=pcs_quantity,
                order_item=instance,
                note=f"Order item created for order {instance.order.order_number}",
            )

        # Handle advanced quantities (advanced_in_ctn and advanced_in_pcs)
        advanced_ctn_quantity = instance.advanced_in_ctn
        advanced_pcs_quantity = instance.advanced_in_pcs

        if advanced_ctn_quantity > 0 or advanced_pcs_quantity > 0:
            # Create transaction for advanced quantities
            StockTransaction.objects.create(
                stock_type=advance_stock_type,
                product=instance.product,
                product_price=instance.price,
                transaction_type=TransactionType.OUT,
                ctn_quantity=advanced_ctn_quantity,
                piece_quantity=advanced_pcs_quantity,
                order_item=instance,
                note=f"Advanced quantity for order {instance.order.order_number}",
            )

        # Handle return quantities (return_in_ctn and return_in_pcs)
        # Returns are IN transactions to Regular Stock (stock coming back in)
        return_ctn_quantity = instance.return_in_ctn
        return_pcs_quantity = instance.return_in_pcs

        if return_ctn_quantity > 0 or return_pcs_quantity > 0:
            # Create IN transaction for returns (stock coming back in)
            StockTransaction.objects.create(
                stock_type=regular_stock_type,
                product=instance.product,
                product_price=instance.price,
                transaction_type=TransactionType.IN,
                ctn_quantity=return_ctn_quantity,
                piece_quantity=return_pcs_quantity,
                order_item=instance,
                note=f"Return quantity for order {instance.order.order_number}",
            )
