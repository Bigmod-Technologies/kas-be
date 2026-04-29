from rest_framework import serializers


class CustomerDueReportFilterSerializer(serializers.Serializer):
    customer = serializers.UUIDField(required=True)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")

        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError(
                {"end_date": "end_date must be greater than or equal to start_date."}
            )

        return attrs


class CustomerDueReportItemSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    entry_type = serializers.ChoiceField(choices=["due_sell", "due_collection"])
    entry_date = serializers.DateField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    note = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    performed_by = serializers.CharField(allow_null=True)
    order_id = serializers.UUIDField(allow_null=True, required=False)
    order_number = serializers.CharField(allow_null=True, required=False)
    created_at = serializers.DateTimeField()
