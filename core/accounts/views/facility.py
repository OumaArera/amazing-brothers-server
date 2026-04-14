from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.shortcuts import get_object_or_404
from ..models import Facility
from ..serializers import FacilitySerializer
from ...common import StandardResultsSetPagination

class FacilityListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        facilities = Facility.objects.all().order_by("-created_at")
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(facilities, request)
        serializer = FacilitySerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = FacilitySerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FacilityRetrieveUpdateDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(Facility, pk=pk)

    # ✅ Retrieve single facility
    def get(self, request, pk):
        facility = self.get_object(pk)
        serializer = FacilitySerializer(facility)
        return Response(serializer.data)

    # ✅ Update facility
    def put(self, request, pk):
        facility = self.get_object(pk)
        serializer = FacilitySerializer(facility, data=request.data, partial=False, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    # ✅ Partial update (PATCH)
    def patch(self, request, pk):
        facility = self.get_object(pk)
        serializer = FacilitySerializer(facility, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    # ✅ Delete facility
    def delete(self, request, pk):
        facility = self.get_object(pk)
        facility.delete()
        return Response({"message": "Facility deleted successfully"}, status=status.HTTP_204_NO_CONTENT)