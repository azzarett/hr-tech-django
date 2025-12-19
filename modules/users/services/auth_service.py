import uuid
from datetime import datetime
from typing import Optional, TypedDict

from modules.users.domain.exceptions import (
    InvalidCredentialsError,
    UserInactiveError,
    UserNotFoundError,
)
from modules.users.domain.models import User, UserAuthToken
from modules.users.repository.user_auth_token_repository import (
    UserAuthTokenRepository,
)
from modules.users.repository.users_repository import UsersRepository


class AuthPayload(TypedDict):
    token: str
    created_at: datetime


class AuthResult(TypedDict):
    auth: AuthPayload
    user: User


class TokenData(TypedDict):
    token: str
    created_at: datetime
    user: User


class AuthService:

    @staticmethod
    def sign_in(email: str, password: str) -> AuthResult:
        user = UsersRepository.get_by_email(email)
        if not user:
            raise UserNotFoundError("User does not exist")
        if not user.is_active:
            raise UserInactiveError("User is inactive")
        if not user.check_password(password):
            raise InvalidCredentialsError("Wrong password")

        UserAuthTokenRepository.revoke_tokens(user.id)

        token_str = str(uuid.uuid4())
        token = UserAuthToken(user=user, token=token_str)
        UserAuthTokenRepository.create(token)

        return {
            "auth": {"token": token.token, "created_at": token.created_at},
            "user": user,
        }

    @staticmethod
    def validate_token(token_str: str) -> Optional[TokenData]:
        token = UserAuthTokenRepository.get_by_token(token_str)
        if not token:
            return None
        user = UsersRepository.get_by_id(token.user_id)
        if not user:
            return None
        return {
            "token": token.token,
            "created_at": token.created_at,
            "user": user,
        }
