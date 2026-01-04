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
    due_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Amount due",
    )
    collection_by_personal_loan = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Amount collected by personal loan",
    )
    deduction_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10.00,
        help_text="Deduction percentage in percentage",
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


class CollectionItem(BaseModel):
    """Model to represent collection items"""

    sales = models.ForeignKey(
        SalesCollection,
        on_delete=models.CASCADE,
        related_name="items",
        help_text="Sales collection this item belongs to",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="collection_items",
        help_text="Product in this collection item",
    )
    price = models.ForeignKey(
        ProductPrice,
        on_delete=models.PROTECT,
        related_name="collection_items_by_price",
        help_text="Price for this collection item",
    )
    order_cnt_qtn = models.IntegerField(default=0, help_text="Carton quantity")
    order_pcs_qtn = models.IntegerField(default=0, help_text="Pieces quantity")
    damage_cnt_qtn = models.IntegerField(default=0, help_text="Damaged carton quantity")
    damage_pcs_qtn = models.IntegerField(default=0, help_text="Damaged pieces quantity")
    free_cnt_qtn = models.IntegerField(default=0, help_text="Free carton quantity")
    free_pcs_qtn = models.IntegerField(default=0, help_text="Free pieces quantity")

    class Meta:
        verbose_name = "Collection Item"
        verbose_name_plural = "Collection Items"
        ordering = ["sales", "product"]

    def __str__(self):
        return f"{self.sales.sales_id} - {self.product.name}"

    @property
    def total_order_amount(self):
        """Calculate total order amount using the price field"""
        if not self.price:
            return Decimal("0.00")

        total = Decimal("0.00")

        total += self.price.ctn_price * self.order_cnt_qtn
        total += self.price.piece_price * self.order_pcs_qtn
        return total

    @property
    def total_damage_amount(self):
        """Calculate total damage amount using the price field with deduction percentage"""
        if not self.price:
            return Decimal("0.00")

        # Calculate base damage amount
        base_total = Decimal("0.00")
        if self.price.ctn_price:
            base_total += Decimal(str(self.price.ctn_price)) * Decimal(
                str(self.damage_cnt_qtn)
            )
        if self.price.piece_price:
            base_total += Decimal(str(self.price.piece_price)) * Decimal(
                str(self.damage_pcs_qtn)
            )

        # Apply deduction percentage from sales collection
        if self.sales and self.sales.deduction_percentage:
            deduction_rate = Decimal(str(self.sales.deduction_percentage)) / Decimal(
                "100.00"
            )
            total = base_total * (Decimal("1.00") - deduction_rate)
        else:
            total = base_total

        return total

    @property
    def total_free_amount(self):
        """Calculate total free amount using the price field with deduction percentage"""
        if not self.price:
            return Decimal("0.00")

        # Calculate base free amount
        base_total = Decimal("0.00")
        if self.price.ctn_price:
            base_total += Decimal(str(self.price.ctn_price)) * Decimal(
                str(self.free_cnt_qtn)
            )
        if self.price.piece_price:
            base_total += Decimal(str(self.price.piece_price)) * Decimal(
                str(self.free_pcs_qtn)
            )

        # Apply deduction percentage from sales collection
        if self.sales and self.sales.deduction_percentage:
            deduction_rate = Decimal(str(self.sales.deduction_percentage)) / Decimal(
                "100.00"
            )
            total = base_total * (Decimal("1.00") - deduction_rate)
        else:
            total = base_total

        return total
