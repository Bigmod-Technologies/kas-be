from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.finance.models import CommissionTransaction
from apps.user.serializers import StaffSerializer

User = get_user_model()


class CommissionTransactionSerializer(serializers.ModelSerializer):
    user_details = StaffSerializer(source="user", read_only=True)

    class Meta:
        model = CommissionTransaction
        fields = [
            "id",
            "user",
            "user_details",
            "transaction_date",
            "amount",
            "note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "user_details", "created_at", "updated_at")
