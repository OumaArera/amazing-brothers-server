from rest_framework import serializers
from ..models.resident import Resident
from ..models.branch import Branch
from .branch import BranchSerializer  # optional if you want nested data

class ResidentSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    branch_address = serializers.CharField(source='branch.address', read_only=True)

    class Meta:
        model = Resident
        fields = '__all__'