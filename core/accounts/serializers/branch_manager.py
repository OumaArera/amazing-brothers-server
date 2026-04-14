from rest_framework import serializers
from ..models import BranchManager

class BranchManagerSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = BranchManager
        fields = [
            "id",
            "user",
            "user_name",
            "branch",
            "full_name",
            "branch_name",
            "created_at",
            "modified_at",
        ]

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}" if obj.user.first_name and obj.user.last_name else ""