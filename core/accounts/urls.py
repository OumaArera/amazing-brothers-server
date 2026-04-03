from django.urls import path
from .views import *


urlpatterns = [
    path("create/", CreateUserView.as_view()),
    path("login/", LoginView.as_view()),
    path("change-password/", ChangePasswordView.as_view()),
    path("forgot-password/", ForgotPasswordView.as_view()),
    path("reset-password/<int:uid>/<str:token>/", ResetPasswordView.as_view()),
    path("refresh/token/", CustomTokenRefreshView.as_view(), name="token_refresh"),
]
