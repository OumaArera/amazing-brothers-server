from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import GroceryRequest
from ..serializers import GroceryRequestSerializer
from ...common import StandardResultsSetPagination


class GroceryRequestListCreateView(generics.ListCreateAPIView):
    serializer_class = GroceryRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = GroceryRequest.objects.all().order_by("-created_at")

        branch_id = self.request.query_params.get("branch_id")
        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)

        return queryset

    def get_serializer_context(self):
        return {"request": self.request}
    

class GroceryRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = GroceryRequest.objects.all()
    serializer_class = GroceryRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "pk"



class GroceryRequestReviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        grocery_request = GroceryRequest.objects.get(pk=pk)

        action = request.data.get("action")

        if action == "approve":
            grocery_request.status = "approved"
            grocery_request.decline_reason = None

        elif action == "decline":
            grocery_request.status = "declined"
            grocery_request.decline_reason = request.data.get("decline_reason")

        elif action == "fulfill":
            grocery_request.status = "fulfilled"

        else:
            return Response(
                {"error": "Invalid action"},
                status=status.HTTP_400_BAD_REQUEST
            )

        grocery_request.save()

        return Response({"message": f"Request {action}d successfully"})
    
