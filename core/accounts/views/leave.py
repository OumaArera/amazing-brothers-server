from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import LeaveRequest
from ..serializers import LeaveRequestSerializer
from ...common import StandardResultsSetPagination


class LeaveRequestListCreateView(generics.ListCreateAPIView):
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user

        # Users only see their own requests
        queryset = LeaveRequest.objects.filter(staff=user).order_by("-created_at")

        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

    def get_serializer_context(self):
        return {"request": self.request}
    

class LeaveRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "pk"

    def get_queryset(self):
        return LeaveRequest.objects.filter(staff=self.request.user)
    


class LeaveRequestReviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        leave = LeaveRequest.objects.get(pk=pk)

        action = request.data.get("action")

        if action == "approve":
            leave.status = "approved"
            leave.decline_reason = None

        elif action == "decline":
            leave.status = "declined"
            leave.decline_reason = request.data.get("decline_reason")

        else:
            return Response(
                {"error": "Invalid action"},
                status=status.HTTP_400_BAD_REQUEST
            )

        leave.save()

        return Response({"message": f"Leave request {action}d successfully"})