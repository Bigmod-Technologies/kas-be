from django.db import models
from django.core.validators import MinValueValidator
from apps.core.models import BaseModel
from .product import Product


class PriceFor(models.TextChoices):
    """Price type choices"""

    PRODUCT = "PRODUCT", "Product"
    PURCHASE = "PURCHASE", "Purchase"
    OFFER = "OFFER", "Offer"


class ProductPrice(BaseModel):
    """
    Model to store different price configurations for products.
    Allows multiple price entries per product for different price types.
    """

    price_for = models.CharField(
        max_length=50,
        choices=PriceFor.choices,
        default=PriceFor.PRODUCT,
        help_text="Type of price (Product, Purchase, Offer)",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="prices",
        help_text="Product this price belongs to",
    )
    ctn_size = models.IntegerField(null=True, blank=True, help_text="Carton size")
    ctn_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Price per carton",
    )
    piece_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Price per piece",
    )
    offer_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Special offer price",
    )
    is_latest = models.BooleanField(
        default=True,
        help_text="Whether this is the latest price for this product and price type",
    )

    class Meta:
        verbose_name = "Product Price"
        verbose_name_plural = "Product Prices"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["product", "price_for", "is_latest"]),
            models.Index(fields=["is_latest"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["product", "price_for"],
                condition=models.Q(is_latest=True),
                name="unique_latest_price_per_product_type",
            )
        ]

    def __str__(self):
        return f"{self.product.name} - {self.get_price_for_display()}"

    def save(self, *args, **kwargs):
        """
        Ensure only one latest price exists per product and price type.
        When setting is_latest=True, set all other prices for the same
        product and price type to is_latest=False.
        """
        if self.is_latest:
            ProductPrice.objects.filter(
                product=self.product, price_for=self.price_for, is_latest=True
            ).exclude(pk=self.pk if self.pk else None).update(is_latest=False)
        super().save(*args, **kwargs)


    @property
    def have_permission_to_delete(self) -> bool:
        # logic will be implement later
        return False