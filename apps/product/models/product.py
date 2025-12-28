from django.db import models
from apps.core.models import BaseModel
from .brand import Brand


class Product(BaseModel):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        IN_ACTIVE = "IN_ACTIVE", "In Active"
        PENDING = "PENDING", "Pending"

    name = models.CharField(max_length=255)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT)
    ctn_size = models.IntegerField(null=True, blank=True)
    ctn_price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    pic_price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    have_offer = models.BooleanField(default=False)
    offer_price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    status = models.CharField(
        max_length=50, choices=Status.choices, default=Status.PENDING
    )
    sku = models.CharField(max_length=150)

    def __str__(self):
        return self.name
