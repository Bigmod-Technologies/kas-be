from decimal import Decimal

from django.db import models
from apps.core.models import BaseModel
from apps.area.models import Area


class CustomerType(models.TextChoices):
    PDF = "PDF", "PDF"
    ODF = "ODF", "ODF"


class Customer(BaseModel):
    """Model to represent customers"""

    name = models.CharField(max_length=255)
    shop_name = models.CharField(max_length=255)
    shop_name_en = models.CharField(max_length=255, null=True, blank=True)
    contact_number = models.CharField(max_length=50, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    area = models.ForeignKey(
        Area,
        on_delete=models.PROTECT,
        related_name="customers",
        null=True,
        blank=True,
        help_text="Area where the customer is located",
    )
    due_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    order_discount_in_persentage = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )
    have_special_discount = models.BooleanField(default=False)
    special_discount_in_persentage = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )
    customer_id = models.CharField(max_length=255, null=True, blank=True)
    fridge_type = models.CharField(
        max_length=50, choices=CustomerType.choices, null=True, blank=True
    )

    @property
    def due_sell(self):
        """Total due sell amount for this customer."""
        from django.db import models as dj_models

        return (
            self.due_sells.aggregate(total=dj_models.Sum("amount"))["total"]
            or Decimal("0.00")
        )

    @property
    def due_collection(self):
        """Total collected amount against due sells for this customer."""
        from django.db import models as dj_models

        return (
            self.due_collections.aggregate(total=dj_models.Sum("amount"))["total"]
            or Decimal("0.00")
        )

    @property
    def balance(self):
        """
        Customer balance =
        total due sell - (opening balance + total collection)
        """
        return (self.opening_balance + self.due_collection) - self.due_sell

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.shop_name}"
