from rest_framework import serializers
from ..models import Appointment, Resident


class AppointmentSerializer(serializers.ModelSerializer):
    resident = serializers.PrimaryKeyRelatedField(
        queryset=Resident.objects.all()
    )

    class Meta:
        model = Appointment
        fields = [
            "id",
            "resident",
            "date_taken",
            "details",
            "type",
            "next_appointment_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

