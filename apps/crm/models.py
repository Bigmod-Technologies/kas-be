from email.policy import default
from django.db import models
from apps.core.models import BaseModel
from apps.area.models import Zone


class Customer(BaseModel):
    """Model to represent customers"""

    name = models.CharField(max_length=255)
    shop_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=50, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    zone = models.ForeignKey(
        Zone,
        on_delete=models.PROTECT,
        related_name="customers",
        null=True,
        blank=True,
        help_text="Zone/area where the customer is located",
    )
    due_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    order_discount_in_persentage = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )
    have_special_discount = models.BooleanField(default=False)
    special_discount_in_persentage = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.shop_name}"
