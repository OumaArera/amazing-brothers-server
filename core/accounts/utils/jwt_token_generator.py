from rest_framework_simplejwt.tokens import RefreshToken

def get_tokens_for_user(user):
    """
    Generates JWT tokens with custom claims:
    - user_id (as string if UUID)
    - email
    - full_name
    - role
    """
    refresh = RefreshToken.for_user(user)

    access_token = refresh.access_token
    # Convert UUID to string
    access_token["user_id"] = str(user.id)
    access_token["email"] = user.email
    access_token["full_name"] = f"{user.first_name} {user.last_name}"
    access_token["role"] = user.role

    return {
        "access": str(access_token),
        "refresh": str(refresh),
    }