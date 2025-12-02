from modules.users.repository.users_repository import UsersRepository
from modules.users.domain.models import User
from modules.users.domain.exceptions import UserNotFoundError
from modules.teams.domain.models import UserTeam
from django.utils import timezone


class UsersService:

    @staticmethod
    def get_me(user: User) -> User:
        return user

    @staticmethod
    def get_one_user(user_id) -> User:
        user = UsersRepository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id={user_id} not found")
        return user

    @staticmethod
    def exists_by_email(email: str) -> bool:
        return UsersRepository.get_by_email(email) is not None

    @staticmethod
    def get_by_email(email: str):
        return UsersRepository.get_by_email(email)

    @staticmethod
    def create_user(email: str, password: str, first_name: str, last_name: str):
        return User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

    @staticmethod
    def get_team_users(team_id: str):
        """Get all users in a team"""
        user_teams = UserTeam.objects.filter(
            team_id=team_id,
            deleted_at__isnull=True
        ).select_related('user')
        
        return [ut.user for ut in user_teams]

    @staticmethod
    def update_me(user: User, data: dict, team_id: str):
        """Update current user profile"""
        from modules.teams.domain.models import Role
        
        # Update user fields
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        
        if 'birth_date' in data:
            user.birth_date = data['birth_date']
        if 'email' in data:
            user.email = data['email']
        if 'phone' in data:
            user.phone = data['phone']
        if 'faculty_id' in data:
            user.faculty_id = data['faculty_id']
        if 'clothes_size' in data:
            user.clothes_size = data['clothes_size']
        if 'city' in data:
            user.city = data['city']
        if 'admission_year' in data:
            user.admission_year = data['admission_year']
        if 'telegram_nick' in data:
            user.telegram_nick = data['telegram_nick']
        
        user.save()
        
        # Update roles for this team
        if 'roles' in data and data['roles']:
            # Delete existing roles for this team
            Role.objects.filter(
                user=user,
                team_id=team_id,
                deleted_at__isnull=True
            ).update(deleted_at=timezone.now())
            
            # Create new roles
            for role_data in data['roles']:
                Role.objects.create(
                    user=user,
                    team_id=team_id,
                    role=role_data.get('role')
                )
        
        # Refresh user data with relations
        return UsersRepository.get_by_id(user.id)

    @staticmethod
    def delete_user(user_id: str, team_id: str, current_user: User):
        """Remove user from team (soft delete)"""
        from modules.teams.domain.models import Role
        
        # Check if current user has permission in this team
        current_user_team = UserTeam.objects.filter(
            user=current_user,
            team_id=team_id,
            deleted_at__isnull=True
        ).first()
        
        if not current_user_team:
            raise ValueError("You are not a member of this team")
        
        # Check if user has captain/vice-captain role or has permission to manage users
        current_user_role = Role.objects.filter(
            user=current_user,
            team_id=team_id,
            deleted_at__isnull=True
        ).first()
        
        is_moderator = current_user_role and current_user_role.role in ["captain", "vice-captain"]
        has_permission = current_user_team.has_permission_manage_users
        
        if not (is_moderator or has_permission):
            raise ValueError("You don't have permission to remove users")
        
        # Find the user team relationship to delete
        user_team = UserTeam.objects.filter(
            user_id=user_id,
            team_id=team_id,
            deleted_at__isnull=True
        ).first()
        
        if not user_team:
            raise UserNotFoundError("User is not in this team")
        
        # Soft delete
        user_team.deleted_at = timezone.now()
        user_team.save()
        
        return user_team
