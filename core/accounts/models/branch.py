import uuid
from django.db import models
from django.conf import settings
from .facility import Facility

class Branch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    address = models.TextField()
    facility = models.ForeignKey(
        Facility,
        on_delete=models.CASCADE,
        related_name="branches"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="branches"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name