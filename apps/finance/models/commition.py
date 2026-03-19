from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from apps.core.models import BaseModel

User = get_user_model()


class CommissionTransaction(BaseModel):
    """
    Ledger-style commission tracking.

    Store one row per commission event per user.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="commission_transactions",
    )
    transaction_date = models.DateField(
        default=date.today,
        help_text="Business date for this commission",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Commission amount (always positive; type defines sign)",
    )
    note = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Commission Transaction"
        verbose_name_plural = "Commission Transactions"
        ordering = ["-transaction_date", "-created_at"]
        indexes = [
            models.Index(fields=["user", "transaction_date"], name="fin_comm_user_date_idx"),
        ]

    def __str__(self) -> str:
        username = getattr(self.user, "username", str(self.user_id))
        return f"{username} commission {self.amount}"
