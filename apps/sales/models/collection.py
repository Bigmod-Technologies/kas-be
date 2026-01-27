from django.db import models
from datetime import date
from django.contrib.auth import get_user_model
from apps.core.models import BaseModel
from apps.product.models import Product, ProductPrice
from apps.crm.models import Customer
from decimal import Decimal

User = get_user_model()


class SalesCollection(BaseModel):
    """Model to represent sales collections"""

    sales_id = models.CharField(
        max_length=150,
        unique=True,
        blank=True,
        editable=False,
        help_text="Unique identifier for the sales collection (auto-generated)",
    )
    sales_date = models.DateField(default=date.today, help_text="Date of the sale")
    sales_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="sales_collections",
        help_text="User who made the sale",
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="customer_sales_collections",
        help_text="Customer for this sale",
    )
    total_sale = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Total sale amount",
    )
    commission_in_percentage = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Commission in percentage",
    )
    special_discount_in_percentage = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Special discount in percentage",
    )
    collection_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Amount collected",
    )

    class Meta:
        verbose_name = "Sales Collection"
        verbose_name_plural = "Sales Collections"
        ordering = ["-sales_date", "sales_id"]

    def save(self, *args, **kwargs):
        """Auto-generate sales_id if not provided"""
        if not self.sales_id:
            from apps.sales.utils import generate_sales_id
            self.sales_id = generate_sales_id()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sales {self.sales_id} - {self.customer.name}"


class DamageItem(BaseModel):
    """Model to represent damage items in sales collections"""

    sales = models.ForeignKey(
        SalesCollection,
        on_delete=models.CASCADE,
        related_name="damage_items",
        help_text="Sales collection this damage item belongs to",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="damage_items",
        help_text="Product in this damage item",
    )
    price = models.ForeignKey(
        ProductPrice,
        on_delete=models.PROTECT,
        related_name="damage_items_by_price",
        help_text="Price for this damage item",
    )
    cnt_qtn = models.IntegerField(default=0, help_text="Carton quantity")
    pcs_qtn = models.IntegerField(default=0, help_text="Pieces quantity")
    deduction_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Deduction percentage in percentage",
    )

    class Meta:
        verbose_name = "Damage Item"
        verbose_name_plural = "Damage Items"
        ordering = ["sales", "product"]

    def __str__(self):
        return f"{self.sales.sales_id} - {self.product.name}"


class FreeItem(BaseModel):
    """Model to represent free items in sales collections"""

    sales = models.ForeignKey(
        SalesCollection,
        on_delete=models.CASCADE,
        related_name="free_items",
        help_text="Sales collection this free item belongs to",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="free_items",
        help_text="Product in this free item",
    )
    price = models.ForeignKey(
        ProductPrice,
        on_delete=models.PROTECT,
        related_name="free_items_by_price",
        help_text="Price for this free item",
    )
    cnt_qtn = models.IntegerField(default=0, help_text="Carton quantity")
    pcs_qtn = models.IntegerField(default=0, help_text="Pieces quantity")

    class Meta:
        verbose_name = "Free Item"
        verbose_name_plural = "Free Items"
        ordering = ["sales", "product"]

    def __str__(self):
        return f"{self.sales.sales_id} - {self.product.name}"

