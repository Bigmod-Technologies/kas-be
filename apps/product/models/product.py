from django.db import models
from django.db.models import Sum, Case, When, IntegerField
from apps.core.models import BaseModel
from .brand import Brand


class Status(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    IN_ACTIVE = "IN_ACTIVE", "In Active"
    PENDING = "PENDING", "Pending"


class Product(BaseModel):

    name = models.CharField(max_length=255)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT)
    have_offer = models.BooleanField(default=False)
    status = models.CharField(
        max_length=50, choices=Status.choices, default=Status.PENDING
    )
    sku = models.CharField(max_length=150, unique=True)
    buy_qty = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    free_qty = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    @property
    def latest_product_price(self):
        return self.prices.filter(is_latest=True, price_for="PRODUCT").first()

    @property
    def total_regular_stock_ctn_quantity(self) -> int:
        """Calculate total carton quantity: sum of IN transactions minus sum of OUT transactions"""
        result = self.stock_transactions.filter(stock_type__name="Regular Stock").aggregate(
            in_total=Sum(
                Case(
                    When(transaction_type="IN", then="ctn_quantity"),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
            out_total=Sum(
                Case(
                    When(transaction_type="OUT", then="ctn_quantity"),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
        )
        in_total = result["in_total"] or 0
        out_total = result["out_total"] or 0
        return in_total - out_total

    @property
    def total_regular_stock_piece_quantity(self) -> int:
        """Calculate total piece quantity: sum of IN transactions minus sum of OUT transactions"""
        result = self.stock_transactions.filter(stock_type__name="Regular Stock").aggregate(
            in_total=Sum(
                Case(
                    When(transaction_type="IN", then="piece_quantity"),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
            out_total=Sum(
                Case(
                    When(transaction_type="OUT", then="piece_quantity"),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
        )
        in_total = result["in_total"] or 0
        out_total = result["out_total"] or 0
        return in_total - out_total

    @property
    def total_main_stock_ctn_quantity(self) -> int:
        """Calculate total carton quantity: sum of IN transactions minus sum of OUT transactions"""
        result = self.stock_transactions.filter(stock_type__name="Main Stock").aggregate(
            in_total=Sum(
                Case(
                    When(transaction_type="IN", then="ctn_quantity"),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
            out_total=Sum(
                Case(
                    When(transaction_type="OUT", then="ctn_quantity"),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
        )
        in_total = result["in_total"] or 0
        out_total = result["out_total"] or 0
        return in_total - out_total

    @property
    def total_main_stock_piece_quantity(self) -> int:
        """Calculate total piece quantity: sum of IN transactions minus sum of OUT transactions"""
        result = self.stock_transactions.filter(stock_type__name="Main Stock").aggregate(
            in_total=Sum(
                Case(
                    When(transaction_type="IN", then="piece_quantity"),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
            out_total=Sum(
                Case(
                    When(transaction_type="OUT", then="piece_quantity"),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
        )
        in_total = result["in_total"] or 0
        out_total = result["out_total"] or 0
        return in_total - out_total

    @property
    def total_free_stock_ctn_quantity(self) -> int:
        """Calculate total carton quantity: sum of IN transactions minus sum of OUT transactions"""
        result = self.stock_transactions.filter(stock_type__name="Free Stock").aggregate(
            in_total=Sum(
                Case(
                    When(transaction_type="IN", then="ctn_quantity"),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
            out_total=Sum(
                Case(
                    When(transaction_type="OUT", then="ctn_quantity"),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
        )
        in_total = result["in_total"] or 0
        out_total = result["out_total"] or 0
        return in_total - out_total

    @property
    def total_free_stock_piece_quantity(self) -> int:
        """Calculate total piece quantity: sum of IN transactions minus sum of OUT transactions"""
        result = self.stock_transactions.filter(stock_type__name="Free Stock").aggregate(
            in_total=Sum(
                Case(
                    When(transaction_type="IN", then="piece_quantity"),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
            out_total=Sum(
                Case(
                    When(transaction_type="OUT", then="piece_quantity"),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
        )
        in_total = result["in_total"] or 0
        out_total = result["out_total"] or 0
        return in_total - out_total

    @property
    def total_damage_stock_ctn_quantity(self) -> int:
        """Calculate total carton quantity: sum of IN transactions minus sum of OUT transactions"""
        result = self.stock_transactions.filter(stock_type__name="Damage Stock").aggregate(
            in_total=Sum(
                Case(
                    When(transaction_type="IN", then="ctn_quantity"),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
            out_total=Sum(
                Case(
                    When(transaction_type="OUT", then="ctn_quantity"),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
        )
        in_total = result["in_total"] or 0
        out_total = result["out_total"] or 0
        return in_total - out_total

    @property
    def total_damage_stock_piece_quantity(self) -> int:
        """Calculate total piece quantity: sum of IN transactions minus sum of OUT transactions"""
        result = self.stock_transactions.filter(stock_type__name="Damage Stock").aggregate(
            in_total=Sum(
                Case(
                    When(transaction_type="IN", then="piece_quantity"),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
            out_total=Sum(
                Case(
                    When(transaction_type="OUT", then="piece_quantity"),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
        )
        in_total = result["in_total"] or 0
        out_total = result["out_total"] or 0
        return in_total - out_total

    @property
    def total_advance_stock_ctn_quantity(self) -> int:
        """Calculate total carton quantity: sum of IN transactions minus sum of OUT transactions"""
        result = self.stock_transactions.filter(stock_type__name="Advance Stock").aggregate(
            in_total=Sum(
                Case(
                    When(transaction_type="IN", then="ctn_quantity"),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
            out_total=Sum(
                Case(
                    When(transaction_type="OUT", then="ctn_quantity"),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
        )
        in_total = result["in_total"] or 0
        out_total = result["out_total"] or 0
        return in_total - out_total

    @property
    def total_advance_stock_piece_quantity(self) -> int:
        """Calculate total piece quantity: sum of IN transactions minus sum of OUT transactions"""
        result = self.stock_transactions.filter(stock_type__name="Advance Stock").aggregate(
            in_total=Sum(
                Case(
                    When(transaction_type="IN", then="piece_quantity"),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
            out_total=Sum(
                Case(
                    When(transaction_type="OUT", then="piece_quantity"),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
        )
        in_total = result["in_total"] or 0
        out_total = result["out_total"] or 0
        return in_total - out_total
