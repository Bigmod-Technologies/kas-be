from django.db import models
from apps.core.models import BaseModel


class Zone(BaseModel):
    """Model to represent different zones/areas for customer categorization"""

    name = models.CharField(max_length=255, unique=True)
    is_archive = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Zone"
        verbose_name_plural = "Zones"
        ordering = ["name"]

    def __str__(self):
        return self.name
