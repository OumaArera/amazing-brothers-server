import uuid
from django.db import models
from django.conf import settings
from .resident import Resident


class Update(models.Model):

    TYPE_CHOICES = [
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("declined", "Declined"),
        ("updated", "Updated"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    resident = models.ForeignKey(
        Resident,
        on_delete=models.CASCADE,
        related_name="updates"
    )

    care_giver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="given_updates"
    )

    notes = models.TextField()

    date_taken = models.DateField()

    type = models.CharField(max_length=10, choices=TYPE_CHOICES)

    weight = models.FloatField()

    weight_deviation = models.FloatField(null=True, blank=True)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending"
    )

    decline_reason = models.TextField(null=True, blank=True)
    reason_not_filled = models.TextField(null=True, blank=True)
    reason_edited = models.TextField(null=True, blank=True)
    reason_filled_late = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_weight_deviation(self):
        last_update = Update.objects.filter(
            resident=self.resident
        ).exclude(id=self.id).order_by("-date_taken").first()

        if last_update:
            return self.weight - last_update.weight
        return 0

    def save(self, *args, **kwargs):
        if not self.pk:  # only calculate on create
            super().save(*args, **kwargs)  # save first to get ID
            self.weight_deviation = self.calculate_weight_deviation()
            super().save(update_fields=["weight_deviation"])
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.resident} - {self.date_taken}"