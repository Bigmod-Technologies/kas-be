from datetime import date

from django.db import models
from django.contrib.auth import get_user_model

from apps.core.models import BaseModel
from apps.crm.models import Customer

User = get_user_model()


class DueSell(BaseModel):
    """Model to represent due sells for customers."""

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="due_sells",
        help_text="Customer for this due sell",
    )
    deliver_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="delivered_due_sells",
        help_text="User who delivered the goods",
    )
    sale_date = models.DateField(
        default=date.today,
        help_text="Date of the sale",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Due amount for this sell",
    )
    note = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about this due sell",
    )

    class Meta:
        verbose_name = "Due Sell"
        verbose_name_plural = "Due Sells"
        ordering = ["-sale_date", "-created_at"]

    def __str__(self):
        return f"DueSell {self.customer.name} - {self.amount}"


