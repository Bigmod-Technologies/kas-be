from rest_framework import serializers
from apps.area.models import Area, WorkingDay


class WorkingDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkingDay
        fields = [
            "id",
            "name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "created_at", "updated_at")


class AreaSerializer(serializers.ModelSerializer):
    zone_name = serializers.CharField(source="zone.name", read_only=True)
    working_days_details = WorkingDaySerializer(many=True, read_only=True, source="working_days")

    class Meta:
        model = Area
        fields = [
            "id",
            "zone",
            "zone_name",
            "name",
            "route_number",
            "working_days",
            "working_days_details",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "zone_name", "working_days_details", "created_at", "updated_at")

