from datetime import date

from django.db import models
from django.contrib.auth import get_user_model

from apps.core.models import BaseModel
from apps.crm.models import Customer

User = get_user_model()


class DueCollection(BaseModel):
    """Model to represent collections (payments) against due sells."""

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="due_collections",
        help_text="Customer who is paying the due amount",
    )
    collected_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="received_due_collections",
        help_text="User who collected the payment",
    )
    collection_date = models.DateField(
        default=date.today,
        help_text="Date of the collection",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Collected amount",
    )
    note = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about this collection",
    )

    class Meta:
        verbose_name = "Due Collection"
        verbose_name_plural = "Due Collections"
        ordering = ["-collection_date", "-created_at"]

    def __str__(self):
        return f"DueCollection {self.customer.name} - {self.amount}"


