from rest_framework import generics, permissions
from ..models import Assessment
from ..serializers import AssessmentSerializer
from ...common import StandardResultsSetPagination


class AssessmentListCreateView(generics.ListCreateAPIView):
    serializer_class = AssessmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = Assessment.objects.all().order_by("-created_at")

        resident_id = self.request.query_params.get("resident_id")
        if resident_id:
            queryset = queryset.filter(resident_id=resident_id)

        return queryset
    

class AssessmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "pk"


