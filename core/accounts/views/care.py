from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.utils import timezone
from django.utils.dateparse import parse_date
from ..models import CareCategory, CareItem, ResidentDailyChart
from ..serializers.care import *
from ...common import StandardResultsSetPagination


class CareCategoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        categories = CareCategory.objects.all().order_by("-created_at")

        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(categories, request)

        serializer = CareCategorySerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = CareCategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=201)


class CareItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        items = CareItem.objects.filter(is_active=True)

        category = request.query_params.get("category")
        if category:
            items = items.filter(category_id=category)

        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(items, request)

        serializer = CareItemSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = CareItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)


class ResidentDailyChartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CreateResidentDailyChartSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        chart = serializer.save()
        return Response({"message": "Chart submitted"}, status=201)



class ResidentDailyChartDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, resident_id, date):
        try:
            chart = ResidentDailyChart.objects.get(
                resident_id=resident_id,
                date=date
            )
        except ResidentDailyChart.DoesNotExist:
            return Response({"error": "No chart found"}, status=404)

        items = chart.items.all()

        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(items, request)

        serializer = ResidentDailyChartItemSerializer(page, many=True)

        return paginator.get_paginated_response({
            "id": chart.id,
            "resident": resident_id,
            "date": date,
            "status": chart.status,
            "rejection_reason": chart.rejection_reason,
            "items": serializer.data
        })
    

class ResidentDailyChartListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        charts = ResidentDailyChart.objects.select_related(
            "resident", "reviewed_by"
        ).all().order_by("-date")

        # 🔹 Filters
        resident = request.query_params.get("resident")
        branch = request.query_params.get("branch")
        date = request.query_params.get("date")
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        status_param = request.query_params.get("status")

        if resident:
            charts = charts.filter(resident_id=resident)

        if branch:
            charts = charts.filter(resident__branch_id=branch)

        if date:
            charts = charts.filter(date=parse_date(date))

        if start_date and end_date:
            charts = charts.filter(
                date__range=[parse_date(start_date), parse_date(end_date)]
            )

        if status_param:
            charts = charts.filter(status=status_param)

        # 🔹 Pagination
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(charts, request)

        serializer = ResidentDailyChartSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    

class ReviewResidentDailyChartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, chart_id):
        try:
            chart = ResidentDailyChart.objects.get(id=chart_id)
        except ResidentDailyChart.DoesNotExist:
            return Response({"error": "Chart not found"}, status=404)

        status_value = request.data.get("status")

        if status_value not in ["approved", "rejected"]:
            return Response({"error": "Invalid status"}, status=400)

        chart.status = status_value
        chart.reviewed_by = request.user
        chart.reviewed_at = timezone.now()

        if status_value == "rejected":
            chart.rejection_reason = request.data.get("rejection_reason", "")
        else:
            chart.rejection_reason = None

        chart.save()

        return Response({"message": f"Chart {status_value} successfully"})