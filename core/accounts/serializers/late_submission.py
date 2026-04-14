from rest_framework import serializers
from ..models.late_submission import LateSubmissionPermission


class LateSubmissionPermissionSerializer(serializers.ModelSerializer):
    expires_at = serializers.DateTimeField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = LateSubmissionPermission
        fields = [
            "id", "branch", "submission_type",
            "starts_at", "duration_seconds", "expires_at", "is_active",
            "reason", "created_by", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]