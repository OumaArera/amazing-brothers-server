from rest_framework import serializers
from ..models import Branch, Facility

class FacilityInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = ["id", "name", "address"]

class BranchSerializer(serializers.ModelSerializer):
    facility = FacilityInfoSerializer(read_only=True)
    facility_id = serializers.UUIDField(write_only=True)  # to accept input

    class Meta:
        model = Branch
        fields = ["id", "name", "address", "facility", "facility_id", "created_at"]

    def create(self, validated_data):
        facility_id = validated_data.pop("facility_id")
        validated_data["facility_id"] = facility_id
        validated_data["created_by"] = self.context['request'].user
        return super().create(validated_data)