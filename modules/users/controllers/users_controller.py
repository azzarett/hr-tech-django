from __future__ import annotations

from typing import Any, Dict

from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from modules.users.authentication import BearerTokenAuthentication
from modules.users.domain.exceptions import (
    InvalidCredentialsError,
    UserInactiveError,
    UserNotFoundError,
)
from modules.users.domain.models import User
from modules.users.permissions import IsBearerAuthenticated
from modules.users.serializers.auth_serializers import SignInSerializer
from modules.users.serializers.users_serializers import UsersSerializer
from modules.users.services.auth_service import AuthService, AuthResult
from modules.users.services.users_service import UsersService


class UsersController(ViewSet):
    authentication_classes = (BearerTokenAuthentication,)
    permission_classes = [IsBearerAuthenticated]

    def get_permissions(self):  # type: ignore[override]
        if getattr(self, "action", "") == "token":
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]

    def token(self, request: Request) -> Response:
        serializer = SignInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated: Dict[str, Any] = getattr(serializer, "validated_data", None) or {}
        email = validated.get("email")
        password = validated.get("password")
        if not email or not password:
            return Response({"detail": "Missing credentials"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            result: AuthResult = AuthService.sign_in(email=email, password=password)
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

    def me(self, request: Request) -> Response:
        user: User = request.user  # type: ignore[assignment]
        token_data = AuthService.validate_token(str(request.auth))

        return Response({
            "user": UsersSerializer(user).data,
            "auth": {
                "token": token_data["token"] if token_data else request.auth,
                "created_at": token_data["created_at"] if token_data else None,
            },
        })

    def retrieve(self, request: Request, pk: str | None = None) -> Response:
        try:
            user = UsersService.get_one_user(pk)
        except UserNotFoundError:
            return Response({"detail": "User not found"}, status=404)
        return Response({"user": UsersSerializer(user).data})

    def list(self, request: Request) -> Response:
        """
        GET /v1/users?team_id=<uuid>&page=<int>
        """
        team_id = request.query_params.get("team_id")
        page = int(request.query_params.get("page", 1))
        
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
                    "current_page": page,
                    "total_pages": 1,
                    "per_page": total_items,
                    "total_items": total_items
                }
            }, status=200)
        except Exception as exc:
            return Response({"detail": str(exc)}, status=400)

    def update_me(self, request: Request) -> Response:
        """
        PATCH /v1/users/me/update?team_id=<uuid>
        """
        team_id = request.query_params.get("team_id")
        if not team_id:
            return Response({"detail": "team_id is required"}, status=400)

        try:
            updated_user = UsersService.update_me(
                user=request.user,  # type: ignore[arg-type]
                data=request.data,
                team_id=team_id
            )
            return Response({"user": UsersSerializer(updated_user).data}, status=200)
        except ValueError as e:
            return Response({"detail": str(e)}, status=400)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)

    def destroy(self, request: Request, pk: str | None = None) -> Response:
        """
        DELETE /v1/users/<uuid>?team_id=<uuid>
        """
        team_id = request.query_params.get("team_id")
        if not team_id:
            return Response({"detail": "team_id is required"}, status=400)

        if not pk:
            return Response({"detail": "user_id is required"}, status=400)

        try:
            UsersService.delete_user(str(pk), team_id, request.user)  # type: ignore[arg-type]
            return Response({"message": "User removed from team"}, status=200)
        except UserNotFoundError as e:
            return Response({"detail": str(e)}, status=404)
        except ValueError as e:
            return Response({"detail": str(e)}, status=403)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)
