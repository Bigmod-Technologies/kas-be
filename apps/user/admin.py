from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "phone_number",
        "nid",
        "dob",
        "monthly_salary",
        "sales_commission_in_percentage",
        "created_at",
    ]
    list_filter = [
        "created_at",
        "updated_at",
        "monthly_salary",
        "sales_commission_in_percentage",
    ]
    search_fields = [
        "user__username",
        "user__email",
        "phone_number",
        "nid",
    ]
    readonly_fields = ["id", "created_at", "updated_at"]
    filter_horizontal = ["areas"]
    fieldsets = (
        ("User Information", {"fields": ("user",)}),
        (
            "Personal Information",
            {
                "fields": (
                    "phone_number",
                    "nid",
                    "dob",
                    "profile_picture",
                )
            },
        ),
        (
            "Business Information",
            {
                "fields": (
                    "monthly_salary",
                    "sales_commission_in_percentage",
                    "areas",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "id",
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )
