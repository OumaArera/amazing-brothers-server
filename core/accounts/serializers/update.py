from rest_framework import serializers
from ..models import Update, Resident


class UpdateSerializer(serializers.ModelSerializer):
    resident_id = serializers.UUIDField(write_only=True)
    care_giver = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Update
        fields = [
            "id",
            "resident",
            "resident_id",
            "care_giver",
            "notes",
            "date_taken",
            "type",
            "weight",
            "weight_deviation",
            "status",
            "decline_reason",
            "reason_not_filled",
            "reason_edited",
            "reason_filled_late",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "resident",
            "weight_deviation",
            "status",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        resident_id = validated_data.pop("resident_id")
        validated_data["resident_id"] = resident_id
        validated_data["care_giver"] = self.context["request"].user
        return super().create(validated_data)