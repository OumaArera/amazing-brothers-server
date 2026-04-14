import uuid
from django.db import models
from django.conf import settings


class LeaveRequest(models.Model):

    STATUS_CHOICES = [
        ('approved', 'Approved'),
        ('declined', 'Declined'),
        ('pending', 'Pending')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="leave_requests"
    )

    reason_for_request = models.TextField()

    start_date = models.DateField()
    end_date = models.DateField()

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )

    decline_reason = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.end_date < self.start_date:
            raise ValueError("End date cannot be before start date")

    def __str__(self):
        return f"{self.staff} - {self.start_date} to {self.end_date}"