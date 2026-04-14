import uuid
from django.db import models
from django.conf import settings
from .resident import Resident


class CareCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="care_categories"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class CareItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        CareCategory,
        on_delete=models.CASCADE,
        related_name="items"
    )
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.category.name} - {self.name}"


class ResidentDailyChart(models.Model):

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    resident = models.ForeignKey(
        Resident,
        on_delete=models.CASCADE,
        related_name="daily_charts"
    )

    date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    rejection_reason = models.TextField(null=True, blank=True)

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_charts"
    )

    reviewed_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_charts"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("resident", "date")


class ResidentDailyChartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chart = models.ForeignKey(
        ResidentDailyChart,
        on_delete=models.CASCADE,
        related_name="items"
    )
    care_item = models.ForeignKey(
        CareItem,
        on_delete=models.CASCADE
    )
    value = models.BooleanField(default=False)

    class Meta:
        unique_together = ("chart", "care_item")

    def __str__(self):
        return f"{self.chart} - {self.care_item.name}"