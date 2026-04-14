import uuid
from django.db import models
from .resident import Resident


class Assessment(models.Model):
    """Assessment scheduling"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    resident = models.ForeignKey(
        Resident,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='assessments'
    )

    assessment_start_date = models.DateField(null=True, blank=True)
    assessment_next_date = models.DateField(null=True, blank=True)

    ncp_start_date = models.DateField(null=True, blank=True)
    ncp_next_date = models.DateField(null=True, blank=True)

    social_worker = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def create_assessment(cls, validated_data):
        return cls.objects.create(**validated_data)

    def __str__(self):
        return f"{self.resident} - {self.assessment_start_date}"