from rest_framework import serializers
from ..models import SleepPattern, SleepLog, Resident


class SleepLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SleepLog
        fields = ["hour", "status"]


class SleepPatternSerializer(serializers.ModelSerializer):
    logs = SleepLogSerializer(many=True)
    resident_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = SleepPattern
        fields = [
            "id",
            "resident",
            "resident_id",
            "date",
            "logs",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["resident", "created_at", "updated_at"]

    def create(self, validated_data):
        logs_data = validated_data.pop("logs")
        resident_id = validated_data.pop("resident_id")

        validated_data["resident"] = Resident.objects.get(id=resident_id)

        pattern = SleepPattern.objects.create(**validated_data)

        for log in logs_data:
            SleepLog.objects.create(sleep_pattern=pattern, **log)

        return pattern