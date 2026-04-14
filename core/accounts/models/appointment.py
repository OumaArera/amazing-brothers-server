import uuid
from django.db import models
from .resident import Resident


class Appointment(models.Model):

    TYPE_CHOICES = [
        ('Primary Care Provider (PCP)', 'Primary Care Provider (PCP)'),
        ('Mental Health Provider / Physician/ Prescriber', 'Mental Health Provider / Physician/ Prescriber'),
        ('Clinician', 'Clinician'),
        ("Peer Support Counsellor", "Peer Support Counsellor"),
        ("Counsellor", "Counsellor"),
        ("Dentist", "Dentist"),
        ("Specialist", "Specialist"),
        ("Other", "Other")
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    resident = models.ForeignKey(
        Resident,
        on_delete=models.CASCADE,
        related_name="appointments"
    )

    date_taken = models.DateField()
    details = models.TextField()

    type = models.CharField(
        max_length=100,
        choices=TYPE_CHOICES
    )

    next_appointment_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.resident} - {self.type} ({self.date_taken})"