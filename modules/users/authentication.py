from __future__ import annotations

from typing import Optional, Tuple

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request

from modules.users.domain.models import User
from modules.users.services.auth_service import AuthService, TokenData


class BearerTokenAuthentication(BaseAuthentication):
    """Simple bearer token authentication using `UserAuthToken` entries."""

    keyword = "Bearer"

    def authenticate(self, request: Request) -> Optional[Tuple[User, str]]:
        header = request.headers.get("Authorization", "")
        if not header:
            return None

        parts = header.split()
        if len(parts) != 2 or parts[0] != self.keyword:
            raise AuthenticationFailed("Invalid Authorization header format. Expected 'Bearer <token>'.")

        token_str = parts[1]
        token_data: Optional[TokenData] = AuthService.validate_token(token_str)
        if not token_data:
            raise AuthenticationFailed("Invalid or expired token.")

        return token_data["user"], token_data["token"]

    def authenticate_header(self, request: Request) -> str:
        return self.keyword
