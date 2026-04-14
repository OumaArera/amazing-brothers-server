import django_filters
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, serializers
from ..models.late_submission import LateSubmissionPermission
from ..serializers import LateSubmissionPermissionSerializer


class LateSubmissionPermissionFilter(django_filters.FilterSet):
    class Meta:
        model = LateSubmissionPermission
        fields = ["branch", "submission_type"]


class LateSubmissionPermissionListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = LateSubmissionPermission.objects.select_related("branch", "created_by")
    serializer_class = LateSubmissionPermissionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = LateSubmissionPermissionFilter

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class LateSubmissionPermissionDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = LateSubmissionPermission.objects.select_related("branch", "created_by")
    serializer_class = LateSubmissionPermissionSerializer
    http_method_names = ["get", "patch", "delete", "head", "options"]


def assert_late_submission_allowed(branch, submission_type, target_date):
    today = timezone.now().date()
    if target_date >= today:
        return
    permission = (
        LateSubmissionPermission.objects
        .filter(branch=branch, submission_type=submission_type, starts_at__lte=timezone.now())
        .order_by("-created_at")
        .first()
    )
    if not permission or not permission.is_active:
        raise serializers.ValidationError("Late submission not permitted for this branch and type.")


