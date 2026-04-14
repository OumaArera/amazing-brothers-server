from rest_framework import serializers
from ..models import LeaveRequest


class LeaveRequestSerializer(serializers.ModelSerializer):
    staff = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = LeaveRequest
        fields = [
            "id",
            "staff",
            "reason_for_request",
            "start_date",
            "end_date",
            "status",
            "decline_reason",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "status",
            "decline_reason",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        validated_data["staff"] = self.context["request"].user
        return super().create(validated_data)