import uuid
from django.db import models
from django.conf import settings
from .resident import Resident


class Vital(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        DECLINED = "declined", "Declined"
        UPDATED = "updated", "Updated"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resident = models.ForeignKey(Resident, on_delete=models.CASCADE, related_name="vitals")
    caregiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="vitals")
    blood_pressure = models.CharField(max_length=100)
    temperature = models.FloatField()
    pulse = models.FloatField()
    oxygen_saturation = models.FloatField()
    pain = models.TextField(null=True, blank=True)
    date_taken = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    decline_reason = models.TextField(null=True, blank=True)
    reason_edited = models.TextField(null=True, blank=True)
    reason_filled_late = models.TextField(null=True, blank=True)
    reason_not_filled = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date_taken"]

    def __str__(self):
        return f"{self.resident} | {self.date_taken:%Y-%m-%d} | {self.status}"