from rest_framework.views import APIView
from datetime import datetime
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenViewBase
from rest_framework import permissions, status
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from ..serializers import *
from ..utils import get_tokens_for_user
from ...common import StandardResultsSetPagination


User = get_user_model()


class CreateUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if not User.objects.filter(role__in=["admin", "supervisor"]).exists():
            return []
        return super().get_permissions()

    def post(self, request):
        if not User.objects.filter(role__in=["admin", "supervisor"]).exists():
            if request.data.get("role") not in ["admin", "supervisor"]:
                return Response(
                    {"error": "First user must be admin or supervisor"},
                    status=400,
                )

        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=201)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        tokens = get_tokens_for_user(user)

        return Response({
            "message": "Login successful",
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "full_name": f"{user.first_name} {user.last_name}"
            },
            "tokens": tokens
        })

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        if not user.check_password(serializer.validated_data["old_password"]):
            return Response({"error": "Wrong password"}, status=400)

        user.set_password(serializer.validated_data["new_password"])
        user.save()

        return Response({"message": "Password changed successfully"})


# class ForgotPasswordView(APIView):
#     def post(self, request):
#         serializer = ForgotPasswordSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         try:
#             user = User.objects.get(email=serializer.validated_data["email"])
#         except User.DoesNotExist:
#             return Response({"message": "If email exists, reset link sent"})

#         token = default_token_generator.make_token(user)

#         return Response({
#             "uid": user.pk,
#             "token": token
#         })

class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = User.objects.get(email=serializer.validated_data["email"])
        except User.DoesNotExist:
            return Response(
                {"message": "If email exists, reset processed"},
                status=status.HTTP_200_OK
            )

        current_year = datetime.now().year
        new_password = f"!Password{current_year}"
        print("Pass: ", new_password)
        user.set_password(new_password)
        user.save()

        return Response({
            "message": "Password reset successful",
            "new_password": new_password
        }, status=status.HTTP_200_OK)

class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request, uid, token):
        try:
            user = User.objects.get(pk=uid)
        except User.DoesNotExist:
            return Response({"error": "Invalid user"}, status=400)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid token"}, status=400)

        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user.set_password(serializer.validated_data["password"])
        user.save()

        return Response({"message": "Password reset successful"})


class CustomTokenRefreshView(TokenViewBase):
    serializer_class = CustomTokenRefreshSerializer


class UsersListView(APIView):
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """
        Get all users, paginated.
        """
        users = User.objects.all().order_by("-created_at")
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(users, request)
        serializer = UserSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)