import uuid
from django.db import models
from .resident import Resident


class SleepPattern(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    resident = models.ForeignKey(
        Resident,
        on_delete=models.CASCADE,
        related_name="sleep_patterns"
    )

    date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["resident", "date"]

    def __str__(self):
        return f"{self.resident} - {self.date}"
    

class SleepLog(models.Model):

    STATUS_CHOICES = [
        ("asleep", "Asleep"),
        ("awake", "Awake"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    sleep_pattern = models.ForeignKey(
        SleepPattern,
        on_delete=models.CASCADE,
        related_name="logs"
    )

    hour = models.PositiveSmallIntegerField()  # 0–23

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES
    )

    class Meta:
        unique_together = ["sleep_pattern", "hour"]

    def __str__(self):
        return f"{self.hour}:00 - {self.status}"