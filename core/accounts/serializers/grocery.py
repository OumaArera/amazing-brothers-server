from rest_framework import serializers
from ..models import GroceryRequest, GroceryItem, Branch


class GroceryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroceryItem
        fields = ["id", "name", "particulars", "quantity"]


class GroceryRequestSerializer(serializers.ModelSerializer):
    items = GroceryItemSerializer(many=True)
    branch_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = GroceryRequest
        fields = [
            "id",
            "branch",
            "branch_id",
            "items",
            "status",
            "decline_reason",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "branch",
            "status",
            "decline_reason",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        branch_id = validated_data.pop("branch_id")

        validated_data["branch"] = Branch.objects.get(id=branch_id)
        validated_data["requested_by"] = self.context["request"].user

        request = GroceryRequest.objects.create(**validated_data)

        for item in items_data:
            GroceryItem.objects.create(request=request, **item)

        return request