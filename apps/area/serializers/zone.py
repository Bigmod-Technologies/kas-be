from rest_framework import serializers
from apps.area.models import Zone
from apps.area.serializers.area import AreaSerializer


class ZoneSerializer(serializers.ModelSerializer):
    areas_display = AreaSerializer(many=True, read_only=True, source="areas")
    # customers = CustomerSerializer(many=True, read_only=True)
    # staff = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Zone
        fields = [
            "id",
            "name",
            "is_archive",
            "areas_display",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "areas_display", "created_at", "updated_at")
