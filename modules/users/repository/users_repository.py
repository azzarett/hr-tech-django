from typing import Optional
from modules.users.domain.models import User


class UsersRepository:

    @staticmethod
    def get_by_id(user_id) -> Optional[User]:
        return User.objects.filter(id=user_id, deleted_at__isnull=True).first()

    @staticmethod
    def get_by_email(email) -> Optional[User]:
        return User.objects.filter(email=email, deleted_at__isnull=True).first()

    @staticmethod
    def save(user: User) -> User:
        user.save()
        return user
