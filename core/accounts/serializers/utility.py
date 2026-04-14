from rest_framework import serializers
from ..models import UtilityRequest, Branch


class UtilityRequestSerializer(serializers.ModelSerializer):
    branch_id = serializers.UUIDField(write_only=True)
    reported_by = serializers.StringRelatedField(read_only=True)
    assigned_to = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = UtilityRequest
        fields = [
            "id",
            "branch",
            "branch_id",
            "title",
            "description",
            "priority",
            "status",
            "reported_by",
            "assigned_to",
            "resolution_notes",
            "rejection_reason",
            "resolved_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "branch",
            "status",
            "reported_by",
            "assigned_to",
            "resolution_notes",
            "rejection_reason",
            "resolved_at",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        branch_id = validated_data.pop("branch_id")

        validated_data["branch"] = Branch.objects.get(id=branch_id)
        validated_data["reported_by"] = self.context["request"].user

        return super().create(validated_data)