from rest_framework import serializers
from ..models import CareCategory, CareItem, ResidentDailyChart, ResidentDailyChartItem


# 🔹 Category Serializer
class CareCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CareCategory
        fields = "__all__"
        read_only_fields = ["id", "created_by", "created_at"]


# 🔹 Item Serializer
class CareItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = CareItem
        fields = ["id", "name", "category", "category_name", "is_active"]


# 🔹 Chart Item Serializer
class ResidentDailyChartItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="care_item.name", read_only=True)

    class Meta:
        model = ResidentDailyChartItem
        fields = ["id", "care_item", "item_name", "value"]


# 🔹 Create Chart Serializer
class CreateResidentDailyChartSerializer(serializers.Serializer):
    resident = serializers.UUIDField()
    date = serializers.DateField()
    items = ResidentDailyChartItemSerializer(many=True)

    def create(self, validated_data):
        request = self.context.get("request")
        items_data = validated_data.pop("items")

        chart = ResidentDailyChart.objects.create(
            resident_id=validated_data["resident"],
            date=validated_data["date"],
            created_by=request.user
        )

        chart_items = [
            ResidentDailyChartItem(
                chart=chart,
                care_item=item["care_item"],
                value=item["value"]
            )
            for item in items_data
        ]

        ResidentDailyChartItem.objects.bulk_create(chart_items)

        return chart
    
    
class ResidentDailyChartSerializer(serializers.ModelSerializer):
    resident_name = serializers.SerializerMethodField()
    branch_name = serializers.SerializerMethodField()

    class Meta:
        model = ResidentDailyChart
        fields = [
            "id",
            "resident",
            "resident_name",
            "branch_name",
            "date",
            "status",
            "rejection_reason",
            "created_at"
        ]

    def get_resident_name(self, obj):
        return f"{obj.resident.first_name} {obj.resident.last_name}"

    def get_branch_name(self, obj):
        return obj.resident.branch.name if obj.resident.branch else None