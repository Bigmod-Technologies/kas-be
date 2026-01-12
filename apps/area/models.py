from django.db import models
from apps.core.models import BaseModel


class WorkingDay(BaseModel):
    name = models.CharField(max_length=255)
    
    class Meta:
        verbose_name = "Working Day"
        verbose_name_plural = "Working Days"
        ordering = ["name"]
    
    def __str__(self):
        return self.name


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

    # @property
    # def customers(self):
    #     from apps.crm.models import Customer

    #     return Customer.objects.filter(zone=self)

    # @property
    # def staff(self):
    #     from apps.user.models import User

    #     return User.objects.filter(profile__zone=self)


class Area(BaseModel):
    zone = models.ForeignKey(Zone, on_delete=models.PROTECT, related_name="areas")
    name = models.CharField(max_length=255)
    route_number = models.CharField(max_length=255)
    working_days = models.ManyToManyField(WorkingDay, related_name="areas_working_days")

    class Meta:
        verbose_name = "Area"
        verbose_name_plural = "Areas"
        ordering = ["name"]

    def __str__(self):
        return self.name
