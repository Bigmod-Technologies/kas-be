from django.db import models
from django.contrib.auth.models import User
from apps.core.models import BaseModel
from django_resized import ResizedImageField


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    nid = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="National ID"
    )
    dob = models.DateField(blank=True, null=True, verbose_name="Date of Birth")
    profile_picture = ResizedImageField(
        size=[300, 300],
        crop=["middle", "center"],
        quality=80,
        upload_to="profile_pictures/",
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.user.username}'s Profile"

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
