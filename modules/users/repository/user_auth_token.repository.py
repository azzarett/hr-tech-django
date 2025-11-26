from typing import Optional
from django.utils import timezone
from modules.users.domain.models import UserAuthToken


class UserAuthTokenRepository:

    @staticmethod
    def create(token: UserAuthToken) -> UserAuthToken:
        token.save()
        return token

    @staticmethod
    def get_by_token(token_str: str) -> Optional[UserAuthToken]:
        return UserAuthToken.objects.filter(token=token_str, deleted_at__isnull=True).first()

    @staticmethod
    def revoke_tokens(user_id):
        UserAuthToken.objects.filter(user_id=user_id, deleted_at__isnull=True).update(
            deleted_at=timezone.now())
