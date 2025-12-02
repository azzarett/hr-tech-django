from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status, permissions

from modules.users.serializers.auth_serializers import SignInSerializer
from modules.users.serializers.users_serializers import UsersSerializer
from modules.users.services.auth_service import AuthService
from modules.users.services.users_service import UsersService
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
            user = UsersService.get_one_user(pk)
        except UserNotFoundError:
            return Response({"detail": "User not found"}, status=404)
        return Response({"user": UsersSerializer(user).data})

    def list(self, request):
        """
        GET /v1/users?team_id=<uuid>&page=<int>
        """
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response({"detail": "Token missing"}, status=401)

        token_str = auth_header.split(" ")[1]
        token_data = AuthService.validate_token(token_str)
        if not token_data:
            return Response({"detail": "Invalid token"}, status=401)

        team_id = request.query_params.get("team_id")
        page = request.query_params.get("page", 1)
        
        if not team_id or team_id == "undefined":
            return Response({
                "users": [],
                "meta": {
                    "current_page": 1,
                    "total_pages": 0,
                    "per_page": 10,
                    "total_items": 0
                }
            }, status=200)

        try:
            users = UsersService.get_team_users(team_id)
            total_items = len(users)
            return Response({
                "users": UsersSerializer(users, many=True).data,
                "meta": {
                    "current_page": int(page),
                    "total_pages": 1,
                    "per_page": total_items,
                    "total_items": total_items
                }
            }, status=200)
        except Exception as exc:
            return Response({"detail": str(exc)}, status=400)

    def update_me(self, request):
        """
        PATCH /v1/users/me/update?team_id=<uuid>
        """
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response({"detail": "Token missing"}, status=401)

        token_str = auth_header.split(" ")[1]
        token_data = AuthService.validate_token(token_str)
        if not token_data:
            return Response({"detail": "Invalid token"}, status=401)

        team_id = request.query_params.get("team_id")
        if not team_id:
            return Response({"detail": "team_id is required"}, status=400)

        try:
            updated_user = UsersService.update_me(
                user=token_data["user"],
                data=request.data,
                team_id=team_id
            )
            return Response({"user": UsersSerializer(updated_user).data}, status=200)
        except ValueError as e:
            return Response({"detail": str(e)}, status=400)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)

    def destroy(self, request, pk=None):
        """
        DELETE /v1/users/<uuid>?team_id=<uuid>
        """
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response({"detail": "Token missing"}, status=401)

        token_str = auth_header.split(" ")[1]
        token_data = AuthService.validate_token(token_str)
        if not token_data:
            return Response({"detail": "Invalid token"}, status=401)

        team_id = request.query_params.get("team_id")
        if not team_id:
            return Response({"detail": "team_id is required"}, status=400)

        try:
            UsersService.delete_user(pk, team_id, token_data["user"])
            return Response({"message": "User removed from team"}, status=200)
        except UserNotFoundError as e:
            return Response({"detail": str(e)}, status=404)
        except ValueError as e:
            return Response({"detail": str(e)}, status=403)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)
