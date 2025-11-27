import uuid
from typing import Optional
from modules.users.repository.users_repository import UsersRepository
from modules.users.repository.user_auth_token_repository import UserAuthTokenRepository
from modules.users.domain.models import UserAuthToken
from modules.users.domain.exceptions import UserNotFoundError, InvalidCredentialsError, UserInactiveError


class AuthService:

    @staticmethod
    def sign_in(email: str, password: str) -> dict:
        user = UsersRepository.get_by_email(email)
        if not user:
            raise UserNotFoundError("User does not exist")
        if not user.is_active:
            raise UserInactiveError("User is inactive")
        if not user.check_password(password):
            raise InvalidCredentialsError("Wrong password")

        # удаляем старые токены
        UserAuthTokenRepository.revoke_tokens(user.id)

        # создаём новый токен
        token_str = str(uuid.uuid4())
        token = UserAuthToken(user=user, token=token_str)
        UserAuthTokenRepository.create(token)

        return {
            "auth": {"token": token.token, "created_at": token.created_at},
            "user": user,
        }

    @staticmethod
    def validate_token(token_str: str) -> Optional[dict]:
        token = UserAuthTokenRepository.get_by_token(token_str)
        if not token:
            return None
        return {"token": token.token, "created_at": token.created_at, "user": token.user}
