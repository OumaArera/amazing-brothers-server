from rest_framework import generics, permissions
from ..models import SleepPattern
from ..serializers import SleepPatternSerializer
from ...common import StandardResultsSetPagination


class SleepPatternListCreateView(generics.ListCreateAPIView):
    serializer_class = SleepPatternSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = SleepPattern.objects.all().order_by("-date")

        resident_id = self.request.query_params.get("resident_id")
        if resident_id:
            queryset = queryset.filter(resident_id=resident_id)

        return queryset
    

class SleepPatternDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SleepPattern.objects.all()
    serializer_class = SleepPatternSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "pk"


