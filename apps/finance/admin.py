from django.contrib import admin

from .models import CommissionTransaction


@admin.register(CommissionTransaction)
class CommissionTransactionAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "transaction_date",
        "amount",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "transaction_date",
        "created_at",
        "updated_at",
        "user",
    ]
    search_fields = [
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
        "note",
    ]
    readonly_fields = ["id", "created_at", "updated_at"]
    raw_id_fields = ["user"]
    date_hierarchy = "transaction_date"
    ordering = ["-transaction_date", "-created_at"]

    fieldsets = (
        (
            "Commission Transaction",
            {
                "fields": (
                    "user",
                    "transaction_date",
                    "amount",
                    "note",
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
