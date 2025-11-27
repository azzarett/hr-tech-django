from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status, permissions

from modules.users.serializers.auth_serializers import SignInSerializer
from modules.users.serializers.users_serializers import UsersSerializer
from modules.users.services.auth_service import AuthService
from modules.users.services.users_service import UserService
from modules.users.domain.exceptions import InvalidCredentialsError, UserInactiveError, UserNotFoundError


class UsersController(ViewSet):
    permission_classes = [permissions.AllowAny]

    def token(self, request):
        serializer = SignInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated = getattr(serializer, "validated_data", None) or {}
        email = validated.get("email")
        password = validated.get("password")
        if not email or not password:
            return Response({"detail": "Missing credentials"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = AuthService.sign_in(email=email, password=password)
        except UserNotFoundError:
            return Response({"detail": "User not found"}, status=404)
        except InvalidCredentialsError:
            return Response({"detail": "Wrong email or password"}, status=401)
        except UserInactiveError:
            return Response({"detail": "User inactive"}, status=403)

        return Response({
            "auth": result["auth"],
            "user": UsersSerializer(result["user"]).data
        })

    def me(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response({"detail": "Token missing"}, status=401)

        token_str = auth_header.split(" ")[1]
        token_data = AuthService.validate_token(token_str)
        if not token_data:
            return Response({"detail": "Invalid token"}, status=401)

        return Response({
            "user": UsersSerializer(token_data["user"]).data,
            "auth": {"token": token_data["token"], "created_at": token_data["created_at"]}
        })

    def retrieve(self, request, pk=None):
        try:
            user = UserService.get_one_user(pk)
        except UserNotFoundError:
            return Response({"detail": "User not found"}, status=404)
        return Response({"user": UsersSerializer(user).data})
