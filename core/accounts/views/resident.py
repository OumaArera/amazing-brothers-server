from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from ..models.resident import Resident
from ..serializers.resident import ResidentSerializer
from ...common import StandardResultsSetPagination

class ResidentListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        residents = Resident.objects.all().order_by('-created_at')
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(residents, request)
        serializer = ResidentSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = ResidentSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ResidentRetrieveUpdateDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, resident_id):
        try:
            return Resident.objects.get(resident_id=resident_id)
        except Resident.DoesNotExist:
            return None

    def get(self, request, resident_id):
        resident = self.get_object(resident_id)
        if not resident:
            return Response({"detail": "Resident not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ResidentSerializer(resident)
        return Response(serializer.data)

    def put(self, request, resident_id):
        resident = self.get_object(resident_id)
        if not resident:
            return Response({"detail": "Resident not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ResidentSerializer(resident, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, resident_id):
        resident = self.get_object(resident_id)
        if not resident:
            return Response({"detail": "Resident not found"}, status=status.HTTP_404_NOT_FOUND)
        resident.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)