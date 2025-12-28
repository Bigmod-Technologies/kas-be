from django.db import models
from apps.core.models import BaseModel


class Brand(BaseModel):

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        IN_ACTIVE = "IN_ACTIVE", "In Active"

    name = models.CharField(max_length=255)
    brand_address = models.CharField(max_length=1255, null=True, blank=True)
    status = models.CharField(
        max_length=50, choices=Status.choices, default=Status.ACTIVE
    )
    note = models.TextField(null=True, blank=True)
    representative_name = models.CharField(max_length=255, null=True, blank=True)
    representative_contact_number = models.CharField(
        max_length=50, null=True, blank=True
    )
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name
