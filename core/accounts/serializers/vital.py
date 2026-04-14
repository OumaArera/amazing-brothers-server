from rest_framework import serializers
from ..models.vital import Vital


class VitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vital
        fields = "__all__"
        read_only_fields = ["id", "caregiver", "status", "created_at", "updated_at"]


class VitalReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vital
        fields = ["status", "decline_reason"]