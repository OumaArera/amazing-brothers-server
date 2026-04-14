from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import Update
from ..serializers import UpdateSerializer
from ...common import StandardResultsSetPagination


class UpdateListCreateView(generics.ListCreateAPIView):
    serializer_class = UpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = Update.objects.all().order_by("-date_taken")

        resident_id = self.request.query_params.get("resident_id")
        if resident_id:
            queryset = queryset.filter(resident_id=resident_id)

        return queryset

    def get_serializer_context(self):
        return {"request": self.request}
    
    
class UpdateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Update.objects.all()
    serializer_class = UpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "pk"

    def get_serializer_context(self):
        return {"request": self.request}
    


class UpdateReviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        update = Update.objects.get(pk=pk)

        action = request.data.get("action")

        if action == "approve":
            update.status = "approved"
            update.decline_reason = None

        elif action == "decline":
            update.status = "declined"
            update.decline_reason = request.data.get("decline_reason")

        else:
            return Response(
                {"error": "Invalid action"},
                status=status.HTTP_400_BAD_REQUEST
            )

        update.save()

        return Response({"message": f"Update {action}d successfully"})