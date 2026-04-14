from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from ..models import BranchManager, Resident
from ..serializers import *
from ...common import StandardResultsSetPagination


class BranchManagerListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        managers = BranchManager.objects.all().order_by("-created_at")
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(managers, request)
        serializer = BranchManagerSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = BranchManagerSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class BranchManagerDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return BranchManager.objects.get(pk=pk)
        except BranchManager.DoesNotExist:
            return None

    def get(self, request, pk):
        manager = self.get_object(pk)
        if not manager:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = BranchManagerSerializer(manager)
        return Response(serializer.data)

    def put(self, request, pk):
        manager = self.get_object(pk)
        if not manager:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = BranchManagerSerializer(manager, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        manager = self.get_object(pk)
        if not manager:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        manager.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Residents in manager's branch
class ResidentsInMyBranchView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            manager = request.user.branch_manager
        except BranchManager.DoesNotExist:
            return Response({"detail": "You are not assigned to any branch."}, status=status.HTTP_403_FORBIDDEN)

        residents = Resident.objects.filter(branch=manager.branch).order_by("-created_at")
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(residents, request)
        serializer = ResidentSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)