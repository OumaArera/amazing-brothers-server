from rest_framework import serializers
from ..models import Assessment, Resident


class AssessmentSerializer(serializers.ModelSerializer):
    resident = serializers.PrimaryKeyRelatedField(
        queryset=Resident.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Assessment
        fields = [
            "id",
            "resident",
            "assessment_start_date",
            "assessment_next_date",
            "ncp_start_date",
            "ncp_next_date",
            "social_worker",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]