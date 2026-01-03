from django.db import models
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
    sku = models.CharField(max_length=150)
    buy_qty = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    free_qty = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    @property
    def latest_product_price(self):
        return self.prices.filter(is_latest=True, price_for="PRODUCT").first()
