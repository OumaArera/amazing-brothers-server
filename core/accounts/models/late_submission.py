import uuid
from datetime import timedelta
from django.db import models
from django.conf import settings
from .branch import Branch


class LateSubmissionPermission(models.Model):
    class Type(models.TextChoices):
        CHART = "chart", "Daily Chart"
        VITALS = "vitals", "Vitals"
        MEDICATION = "medication", "Medication"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="late_permissions")
    submission_type = models.CharField(max_length=20, choices=Type.choices)
    starts_at = models.DateTimeField()
    duration_seconds = models.PositiveIntegerField()
    reason = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def expires_at(self):
        return self.starts_at + timedelta(seconds=self.duration_seconds)

    @property
    def is_active(self):
        from django.utils import timezone
        now = timezone.now()
        return self.starts_at <= now <= self.expires_at

    def __str__(self):
        return f"{self.branch.name} | {self.submission_type} | active={self.is_active}"