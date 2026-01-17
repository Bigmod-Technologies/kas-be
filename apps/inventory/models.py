from django.db import models
from apps.core.models import BaseModel
from apps.product.models import Product
from django.db.models import Sum
from decimal import Decimal


class StockType(BaseModel):
    """Model to represent different types of stock locations or categories"""

    name = models.CharField(max_length=150, unique=True)

    class Meta:
        verbose_name = "Stock Type"
        verbose_name_plural = "Stock Types"
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def total_ctn_quantity(self) -> int:
        # Sum IN transactions
        in_total = (
            self.transactions.filter(transaction_type="IN").aggregate(
                total=Sum("ctn_quantity")
            )["total"]
            or 0
        )

        # Subtract OUT transactions
        out_total = (
            self.transactions.filter(transaction_type="OUT").aggregate(
                total=Sum("ctn_quantity")
            )["total"]
            or 0
        )

        return in_total - out_total

    @property
    def total_piece_quantity(self) -> int:
        # Sum IN transactions
        in_total = (
            self.transactions.filter(transaction_type="IN").aggregate(
                total=Sum("piece_quantity")
            )["total"]
            or 0
        )

        # Subtract OUT transactions
        out_total = (
            self.transactions.filter(transaction_type="OUT").aggregate(
                total=Sum("piece_quantity")
            )["total"]
            or 0
        )

        return in_total - out_total


class TransactionType(models.TextChoices):
    """Transaction type choices"""

    IN = "IN", "In"
    OUT = "OUT", "Out"


class StockTransaction(BaseModel):
    """Model to track stock transactions (in/out) and transfers"""

    stock_type = models.ForeignKey(
        StockType,
        on_delete=models.PROTECT,
        related_name="transactions",
        help_text="Type of stock location/category",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="stock_transactions",
        help_text="Product involved in the transaction",
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices,
        help_text="Type of transaction: IN or OUT",
    )
    ctn_quantity = models.PositiveIntegerField(
        default=0, help_text="Carton quantity for this transaction"
    )
    piece_quantity = models.PositiveIntegerField(
        default=0, help_text="Piece quantity for this transaction"
    )
    have_transfer = models.BooleanField(
        default=False, help_text="Whether this transaction involves a transfer"
    )
    transfer_from = models.ForeignKey(
        StockType,
        on_delete=models.PROTECT,
        related_name="transfers_from",
        null=True,
        blank=True,
        help_text="Source stock type for transfer (if applicable)",
    )
    transfer_to = models.ForeignKey(
        StockType,
        on_delete=models.PROTECT,
        related_name="transfers_to",
        null=True,
        blank=True,
        help_text="Destination stock type for transfer (if applicable)",
    )
    note = models.TextField(
        blank=True, help_text="Additional notes about the transaction"
    )

    batch_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Batch number for this transaction",
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Unit price for this transaction",
    )

    @property
    def total_price(self) -> Decimal:
        return self.unit_price * (self.ctn_quantity + self.piece_quantity)

    class Meta:
        verbose_name = "Stock Transaction"
        verbose_name_plural = "Stock Transactions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["stock_type", "transaction_type"]),
            models.Index(fields=["product"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.get_transaction_type_display()} - {self.stock_type.name}"
