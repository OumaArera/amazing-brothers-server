from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        # Standard refresh validation
        refresh_token = attrs["refresh"]
        refresh = RefreshToken(refresh_token)

        # Get user
        user_id = str(refresh["user_id"]) if "user_id" in refresh else None
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found for refresh token")

        # Add custom claims
        access_token = refresh.access_token
        access_token["user_id"] = str(user.id)
        access_token["email"] = user.email
        access_token["full_name"] = f"{user.first_name} {user.last_name}"
        access_token["role"] = user.role

        return {
            "access": str(access_token),
            "refresh": str(refresh),
        }