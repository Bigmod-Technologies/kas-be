from decimal import Decimal

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.inventory.models import StockTransaction, StockType, TransactionType
from apps.sales.models import DamageOrderItem, FreeOfferItem, OrderItem


def _get_stock_type(name: str) -> StockType:
    """Get StockType by name (cached per request via ORM)."""
    return StockType.objects.get(name=name)


def _get_prices(item):
    """Extract product_price, ctn_price and piece_price from order item."""
    if not item.price:
        return {"product_price": None, "ctn_price": 0, "piece_price": 0}
    return {
        "product_price": item.price,
        "ctn_price": item.price.ctn_price or Decimal("0"),
        "piece_price": item.price.piece_price or Decimal("0"),
    }


def _get_damage_prices(damage_order_item):
    """
    Get ctn_price and piece_price for a DamageOrderItem, applying
    inventory_damage_deduction_percent when set.
    """
    base = _get_prices(damage_order_item)
    ctn_price = base["ctn_price"]
    piece_price = base["piece_price"]

    percent = getattr(
        damage_order_item, "inventory_damage_deduction_percent", None
    )
    if percent is not None and percent > 0:
        factor = Decimal("1") - (Decimal(str(percent)) / Decimal("100"))
        ctn_price = ctn_price * factor
        piece_price = piece_price * factor

    return {
        "product_price": base["product_price"],
        "ctn_price": ctn_price,
        "piece_price": piece_price,
    }


def _create_stock_transaction(
    *,
    stock_type_name: str,
    product,
    transaction_type: str,
    ctn_quantity: int,
    piece_quantity: int,
    note: str,
    order_item=None,
    damage_order_item=None,
    free_offer_item=None,
    product_price=None,
    ctn_price=0,
    piece_price=0,
):
    """Create a StockTransaction with common kwargs."""
    stock_type = _get_stock_type(stock_type_name)
    return StockTransaction.objects.create(
        stock_type=stock_type,
        product=product,
        product_price=product_price,
        transaction_type=transaction_type,
        ctn_quantity=ctn_quantity,
        piece_quantity=piece_quantity,
        ctn_price=ctn_price,
        piece_price=piece_price,
        note=note,
        order_item=order_item,
        damage_order_item=damage_order_item,
        free_offer_item=free_offer_item,
    )


@receiver(post_save, sender=OrderItem)
def create_stock_transaction_on_order_item_created(sender, instance, created, **kwargs):
    """
    Create StockTransaction when an OrderItem is created.

    Case 1: Net quantity (quantity - return) → OUT from Regular Stock
    Case 2: Advanced quantity → IN to Advance Stock
    """
    if not created:
        return

    prices = _get_prices(instance)
    order_ref = instance.order.order_number

    # Case 1: Regular stock OUT (net quantity)
    net_ctn = instance.quantity_in_ctn - instance.return_in_ctn
    net_pcs = instance.quantity_in_pcs - instance.return_in_pcs
    if net_ctn > 0 or net_pcs > 0:
        _create_stock_transaction(
            stock_type_name="Regular Stock",
            product=instance.product,
            transaction_type=TransactionType.OUT.value,
            ctn_quantity=net_ctn,
            piece_quantity=net_pcs,
            note=f"Net quantity (quantity - return) for order {order_ref}",
            order_item=instance,
            **prices,
        )

    # Case 2: Advance stock IN
    adv_ctn = instance.advanced_in_ctn
    adv_pcs = instance.advanced_in_pcs
    if adv_ctn > 0 or adv_pcs > 0:
        _create_stock_transaction(
            stock_type_name="Advance Stock",
            product=instance.product,
            transaction_type=TransactionType.IN.value,
            ctn_quantity=adv_ctn,
            piece_quantity=adv_pcs,
            note=f"Advanced quantity for order {order_ref}",
            order_item=instance,
            **prices,
        )


@receiver(post_save, sender=DamageOrderItem)
def create_stock_transaction_on_damage_order_item_created(
    sender, instance, created, **kwargs
):
    """Create StockTransaction when a DamageOrderItem is created (IN to Damage Stock).
    ctn_price and piece_price are stored with inventory_damage_deduction_percent applied.
    """
    if not created:
        return

    ctn = instance.quantity_in_ctn
    pcs = instance.quantity_in_pcs
    if ctn <= 0 and pcs <= 0:
        return

    note = f"Damaged quantity for order {instance.order.order_number}"
    if instance.damage_reason:
        note += f" - {instance.damage_reason}"

    _create_stock_transaction(
        stock_type_name="Damage Stock",
        product=instance.product,
        transaction_type=TransactionType.IN.value,
        ctn_quantity=ctn,
        piece_quantity=pcs,
        note=note,
        damage_order_item=instance,
        **_get_damage_prices(instance),
    )


@receiver(post_save, sender=FreeOfferItem)
def create_stock_transaction_on_free_offer_item_created(
    sender, instance, created, **kwargs
):
    """Create StockTransaction when a FreeOfferItem is created (OUT from Free Stock)."""
    if not created:
        return

    ctn = instance.quantity_in_ctn
    pcs = instance.quantity_in_pcs
    if ctn <= 0 and pcs <= 0:
        return

    _create_stock_transaction(
        stock_type_name="Free Stock",
        product=instance.product,
        transaction_type=TransactionType.OUT.value,
        ctn_quantity=ctn,
        piece_quantity=pcs,
        note=f"Free offer quantity for order {instance.order.order_number}",
        free_offer_item=instance,
        **_get_prices(instance),
    )
