import uuid
from django.db import models
from ..models import Branch

class Resident(models.Model):
    """Create residents"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=255)
    middle_names = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    diagnosis = models.TextField(null=True, blank=True, default=None)
    allergies = models.TextField(null=True, blank=True, default=None)
    physician_name = models.CharField(max_length=255)
    pcp_or_doctor = models.CharField(max_length=255)
    clinician = models.CharField(max_length=255, null=True, blank=True, default=None)
    branch = models.ForeignKey(
        Branch,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='residents'
    )
    room = models.CharField(max_length=255, null=True, blank=True, default=None)
    cart = models.CharField(max_length=255, null=True, blank=True, default=None)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    @classmethod
    def create_resident(cls, validated_data):
        """
        Create a new resident instance from validated data.
        """
        return cls(**validated_data)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"