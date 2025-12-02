from django.conf import settings
from django.contrib.auth.hashers import make_password

from modules.invitations.repository.invitations_repository import InvitationsRepository
from modules.invitations.domain.exceptions import (
    InvitationNotFoundError,
    InvitationInvalidError,
    InvitationEmailMismatchError,
    EmailAlreadyExistsError,
)
from modules.users.services.users_service import UsersService
from modules.teams.domain.models import UserTeam, Role


class InvitationsService:

    @staticmethod
    def create_invitation(team_id, created_by, dto):
        invitation = InvitationsRepository.create(
            team_id=team_id,
            created_by=created_by,
            email=dto["email"],
            single_use=dto.get("single_use", True),
            is_captain=dto.get("is_captain", False),
            has_permission_manage_users=dto.get("has_permission_manage_users", False),
            has_permission_manage_projects=dto.get("has_permission_manage_projects", False),
        )

        frontend = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
        invite_url = f"{frontend}/invite/{invitation.token}"

        return invitation, invite_url

    @staticmethod
    def get_invitation_by_token_without_status_check(token):
        invitation = InvitationsRepository.find_by_token(token)
        if not invitation:
            raise InvitationNotFoundError("Invitation not found")

        return invitation

    @staticmethod
    def get_invitation_by_token(token):
        invitation = InvitationsRepository.find_by_token(token)
        if not invitation:
            raise InvitationNotFoundError("Invitation not found")

        if invitation.status != invitation.STATUS_PENDING:
            raise InvitationInvalidError(f"Invitation is {invitation.status}")

        return invitation

    @staticmethod
    def check_user_exists(email):
        return UsersService.exists_by_email(email)

    @staticmethod
    def accept_invitation(token):
        invitation = InvitationsService.get_invitation_by_token(token)

        user = UsersService.get_by_email(invitation.email)
        if not user:
            raise EmailAlreadyExistsError("User must register first")

        InvitationsService._attach_user_to_team(user, invitation)

        InvitationsRepository.update_status(invitation, invitation.STATUS_ACCEPTED)

    @staticmethod
    def register_user_by_invitation(token, data):
        invitation = InvitationsService.get_invitation_by_token(token)

        if data["email"] != invitation.email:
            raise InvitationEmailMismatchError("Email does not match invitation")

        if UsersService.exists_by_email(data["email"]):
            raise EmailAlreadyExistsError("User already exists")

        user = UsersService.create_user(
            email=data["email"],
            password=make_password(data["password"]),
            first_name=data["first_name"],
            last_name=data["last_name"],
        )

        InvitationsService._attach_user_to_team(user, invitation)

        InvitationsRepository.update_status(invitation, invitation.STATUS_ACCEPTED)

        return user

    @staticmethod
    def cancel_invitation(invitation_id):
        invitation = InvitationsRepository.find_by_id(invitation_id)
        if not invitation:
            raise InvitationNotFoundError("Invitation not found")

        InvitationsRepository.update_status(invitation, invitation.STATUS_CANCELLED)

    @staticmethod
    def get_team_invitations(team_id):
        return InvitationsRepository.find_by_team_id(team_id)

    @staticmethod
    def _attach_user_to_team(user, invitation):
        """
        Creates Role/UserTeam with correct flags.
        """
        # Check if user is already in the team
        existing_membership = UserTeam.objects.filter(
            team_id=invitation.team_id,
            user=user,
            deleted_at__isnull=True
        ).first()

        if existing_membership:
            # User already in team, just return
            return

        if invitation.is_captain:
            Role.objects.create(
                team_id=invitation.team_id,
                user=user,
                role="Captain",
            )

            UserTeam.objects.create(
                team_id=invitation.team_id,
                user=user,
                has_permission_manage_users=True,
                has_permission_manage_projects=True,
            )
        else:
            UserTeam.objects.create(
                team_id=invitation.team_id,
                user=user,
                has_permission_manage_users=invitation.has_permission_manage_users,
                has_permission_manage_projects=invitation.has_permission_manage_projects,
            )