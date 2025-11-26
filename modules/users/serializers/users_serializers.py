from modules.users.repository.users_repository import UserRepository
from modules.users.domain.models import User
from modules.users.domain.exceptions import UserNotFoundError


class UserService:

    @staticmethod
    def get_me(user: User) -> User:
        return user

    @staticmethod
    def get_one_user(user_id) -> User:
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id={user_id} not found")
        return user
