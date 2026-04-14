from django.db import models
from django.conf import settings

class Facility(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    address = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="facilities"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name