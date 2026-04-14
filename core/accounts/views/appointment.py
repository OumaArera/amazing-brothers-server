from rest_framework import generics, permissions
from ..models import Appointment
from ..serializers import AppointmentSerializer
from ...common import StandardResultsSetPagination


class AppointmentListCreateView(generics.ListCreateAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = Appointment.objects.all().order_by("-date_taken")

        resident_id = self.request.query_params.get("resident_id")
        if resident_id:
            queryset = queryset.filter(resident_id=resident_id)

        return queryset
    

class AppointmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "pk"


