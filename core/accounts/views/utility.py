from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from ..models import UtilityRequest
from ..serializers import UtilityRequestSerializer
from ...common import StandardResultsSetPagination


class UtilityRequestListCreateView(generics.ListCreateAPIView):
    serializer_class = UtilityRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = UtilityRequest.objects.all().order_by("-created_at")

        branch_id = self.request.query_params.get("branch_id")
        status = self.request.query_params.get("status")

        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)

        if status:
            queryset = queryset.filter(status=status)

        return queryset

    def get_serializer_context(self):
        return {"request": self.request}
    

class UtilityRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UtilityRequest.objects.all()
    serializer_class = UtilityRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "pk"



class UtilityRequestActionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        utility = UtilityRequest.objects.get(pk=pk)

        action = request.data.get("action")

        if action == "acknowledge":
            utility.status = "acknowledged"

        elif action == "start":
            utility.status = "in_progress"
            utility.assigned_to = request.user

        elif action == "resolve":
            utility.status = "resolved"
            utility.resolution_notes = request.data.get("resolution_notes")
            utility.resolved_at = timezone.now()

        elif action == "close":
            utility.status = "closed"

        elif action == "reject":
            utility.status = "rejected"
            utility.rejection_reason = request.data.get("rejection_reason")

        else:
            return Response(
                {"error": "Invalid action"},
                status=status.HTTP_400_BAD_REQUEST
            )

        utility.save()

        return Response({"message": f"Utility request {action}d successfully"})