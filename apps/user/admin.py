from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "phone_number", "nid", "dob"]
    list_filter = ["created_at", "updated_at"]
    search_fields = ["user__username", "user__email", "phone_number", "nid"]
    readonly_fields = ["id", "created_at", "updated_at"]
