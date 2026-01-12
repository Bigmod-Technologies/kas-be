from rest_framework import serializers
from apps.area.models import Zone
from apps.crm.serializers import CustomerSerializer
from apps.user.serializers.staff import UserSerializer


class ZoneSerializer(serializers.ModelSerializer):
    customers = CustomerSerializer(many=True, read_only=True)
    staff = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Zone
        fields = [
            "id",
            "name",
            "is_archive",
            "customers",
            "staff",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "customers", "created_at", "updated_at")
