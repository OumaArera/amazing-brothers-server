import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions
from ..models.vital import Vital
from ..serializers.vital import VitalSerializer, VitalReviewSerializer


class VitalFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name="date_taken", lookup_expr="date__gte")
    date_to = django_filters.DateFilter(field_name="date_taken", lookup_expr="date__lte")

    class Meta:
        model = Vital
        fields = ["resident", "caregiver", "status", "date_from", "date_to", "date_taken"]


class VitalListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Vital.objects.select_related("resident", "caregiver")
    serializer_class = VitalSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = VitalFilter

    def perform_create(self, serializer):
        serializer.save(caregiver=self.request.user)


class VitalDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Vital.objects.select_related("resident", "caregiver")
    serializer_class = VitalSerializer
    http_method_names = ["get", "patch", "delete", "head", "options"]


class VitalReviewView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Vital.objects.all()
    serializer_class = VitalReviewSerializer
    http_method_names = ["patch", "head", "options"]

