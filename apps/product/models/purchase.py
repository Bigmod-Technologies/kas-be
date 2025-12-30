from django.db import models
from django.core.validators import MinValueValidator
from apps.core.models import BaseModel
from .suplier import Supplier
from .product import Product


class PurchaseStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    DUE = "DUE", "Due"
    PAID = "PAID", "Paid"


class Unit(models.TextChoices):
    CTN = "CTN", "CTN"
    PICS = "PICs", "PICs"


class Purchase(BaseModel):
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="purchases",
        help_text="Supplier for this purchase"
    )
    purchase_date = models.DateField(
        help_text="Date of the purchase"
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Total amount of the purchase"
    )
    paid_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Amount paid for this purchase"
    )
    due_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Amount due for this purchase"
    )
    status = models.CharField(
        max_length=50,
        choices=PurchaseStatus.choices,
        default=PurchaseStatus.PENDING,
        help_text="Status of the purchase"
    )
    note = models.TextField(
        null=True,
        blank=True,
        help_text="Additional notes for this purchase"
    )
    voucher_number = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        help_text="Voucher number for this purchase"
    )

    class Meta:
        verbose_name = "Purchase"
        verbose_name_plural = "Purchases"
        ordering = ["-purchase_date", "-created_at"]
        indexes = [
            models.Index(fields=["supplier", "purchase_date"]),
            models.Index(fields=["status"]),
            models.Index(fields=["voucher_number"]),
        ]

    def __str__(self):
        return f"Purchase #{self.voucher_number or self.id} - {self.supplier.brand_name}"


class PurchaseItem(BaseModel):
    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name="items",
        help_text="Purchase this item belongs to"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="purchase_items",
        help_text="Product in this purchase item"
    )
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Quantity of the product"
    )
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Price per unit"
    )
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        null=True,
        blank=True,
        help_text="Total price (quantity * unit_price)"
    )
    unit = models.CharField(
        max_length=50,
        choices=Unit.choices,
        help_text="Unit of measurement"
    )

    class Meta:
        verbose_name = "Purchase Item"
        verbose_name_plural = "Purchase Items"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["purchase", "product"]),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.quantity} {self.get_unit_display()}"

    def save(self, *args, **kwargs):
        """Calculate total_price if not provided"""
        if not self.total_price:
            self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

