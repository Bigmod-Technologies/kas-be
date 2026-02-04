from django.db import models
from datetime import date
from decimal import Decimal
from django.contrib.auth import get_user_model
from apps.core.models import BaseModel
from apps.product.models import Product, ProductPrice

User = get_user_model()


class Shift(models.TextChoices):
    MORNING = "MORNING", "MORNING"
    EVENING = "EVENING", "EVENING"


class OrderDelivery(BaseModel):
    """Model to represent order deliveries"""

    order_number = models.CharField(
        max_length=255, unique=True, blank=True, editable=False
    )
    order_date = models.DateField(default=date.today)
    order_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="orderorder_by",
        help_text="User who placed the order",
    )
    narration = models.TextField(
        blank=True, null=True, help_text="Additional notes or narration for the order"
    )
    cash_sell_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Cash sell amount for the order"
    )

    class Meta:
        verbose_name = "Order Delivery"
        verbose_name_plural = "Order Deliveries"
        ordering = ["-order_date", "order_number"]

    def save(self, *args, **kwargs):
        """Auto-generate order number if not provided"""
        if not self.order_number:
            from apps.sales.utils import generate_order_number

            self.order_number = generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.order_number} - {self.order_by.username}"


class OrderItem(BaseModel):
    """Model to represent order items"""

    order = models.ForeignKey(
        OrderDelivery,
        on_delete=models.CASCADE,
        related_name="items",
        help_text="Order this item belongs to",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items",
        help_text="Product in this order item",
    )
    price = models.ForeignKey(
        ProductPrice,
        on_delete=models.PROTECT,
        related_name="order_items_by_price",
        help_text="Price in this order item",
    )
    shift = models.CharField(
        max_length=50,
        choices=Shift.choices,
        help_text="Shift: M (Morning) or E (Evening)",
    )
    quantity_in_ctn = models.IntegerField(default=0, help_text="Quantity in carton")
    quantity_in_pcs = models.IntegerField(default=0, help_text="Quantity in pieces")
    advanced_in_ctn = models.IntegerField(
        default=0, help_text="Advanced quantity in carton"
    )
    advanced_in_pcs = models.IntegerField(
        default=0, help_text="Advanced quantity in pieces"
    )
    return_in_ctn = models.IntegerField(
        default=0, help_text="Return quantity in carton"
    )
    return_in_pcs = models.IntegerField(
        default=0, help_text="Return quantity in pieces"
    )

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
        ordering = ["order", "product"]

    @property
    def total_amount(self):
        """Calculate total amount using the price field"""
        if not self.price:
            return Decimal("0.00")

        total = Decimal("0.00")

        # Calculate net quantity (quantity + advanced - return)
        net_ctn = self.quantity_in_ctn + self.advanced_in_ctn - self.return_in_ctn
        net_pcs = self.quantity_in_pcs + self.advanced_in_pcs - self.return_in_pcs

        # Calculate amount for cartons (handles both positive and negative net quantities)
        if self.price.ctn_price and net_ctn != 0:
            total += Decimal(str(net_ctn)) * self.price.ctn_price

        # Calculate amount for pieces (handles both positive and negative net quantities)
        if self.price.piece_price and net_pcs != 0:
            total += Decimal(str(net_pcs)) * self.price.piece_price

        return total

    def __str__(self):
        return f"{self.order.order_number} - {self.product.name} ({self.shift})"


class DamageOrderItem(BaseModel):
    """Model to represent damaged order items"""

    order = models.ForeignKey(
        OrderDelivery,
        on_delete=models.CASCADE,
        related_name="damage_items",
        help_text="Order this damaged item belongs to",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="damage_order_items",
        help_text="Product in this damaged order item",
    )
    price = models.ForeignKey(
        ProductPrice,
        on_delete=models.PROTECT,
        related_name="damage_order_items_by_price",
        help_text="Price in this damaged order item",
    )
    quantity_in_ctn = models.IntegerField(
        default=0, help_text="Damaged quantity in carton"
    )
    quantity_in_pcs = models.IntegerField(
        default=0, help_text="Damaged quantity in pieces"
    )
    damage_reason = models.TextField(
        blank=True, null=True, help_text="Reason for the damage"
    )

    class Meta:
        verbose_name = "Damage Order Item"
        verbose_name_plural = "Damage Order Items"
        ordering = ["order", "product"]

    @property
    def total_amount(self):
        """Calculate total amount of damaged items using the price field"""
        if not self.price:
            return Decimal("0.00")

        total = Decimal("0.00")

        # Calculate amount for damaged cartons
        if self.price.ctn_price and self.quantity_in_ctn != 0:
            total += Decimal(str(self.quantity_in_ctn)) * self.price.ctn_price

        # Calculate amount for damaged pieces
        if self.price.piece_price and self.quantity_in_pcs != 0:
            total += Decimal(str(self.quantity_in_pcs)) * self.price.piece_price

        return total

    def __str__(self):
        return f"{self.order.order_number} - {self.product.name} (Damage)"


class FreeOfferItem(BaseModel):
    """Model to represent free offer items"""

    order = models.ForeignKey(
        OrderDelivery,
        on_delete=models.CASCADE,
        related_name="free_offer_items",
        help_text="Order this free offer item belongs to",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="free_offer_order_items",
        help_text="Product in this free offer item",
    )
    price = models.ForeignKey(
        ProductPrice,
        on_delete=models.PROTECT,
        related_name="free_offer_order_items_by_price",
        help_text="Price in this free offer item",
    )
    quantity_in_ctn = models.IntegerField(
        default=0, help_text="Free offer quantity in carton"
    )
    quantity_in_pcs = models.IntegerField(
        default=0, help_text="Free offer quantity in pieces"
    )

    class Meta:
        verbose_name = "Free Offer Item"
        verbose_name_plural = "Free Offer Items"
        ordering = ["order", "product"]

    @property
    def total_amount(self):
        """Calculate total amount of free offer items (should be 0 as it's free)"""
        # Free offers have zero value
        return Decimal("0.00")

    def __str__(self):
        return f"{self.order.order_number} - {self.product.name} (Free Offer)"