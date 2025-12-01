from django.conf import settings
from django.contrib.auth.hashers import make_password

from modules.invitations.repository.invitations_repository import InvitationsRepository
from modules.invitations.domain.exceptions import (
    InvitationNotFoundError,
    InvitationInvalidError,
    InvitationEmailMismatchError,
    EmailAlreadyExistsError,
)
from modules.users.services.user_service import UserService
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

        frontend = getattr(settings, "FRONTEND_URL", "http://localhost:3000")
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
        return UserService.exists_by_email(email)

    @staticmethod
    def accept_invitation(token):
        invitation = InvitationsService.get_invitation_by_token(token)

        user = UserService.get_by_email(invitation.email)
        if not user:
            raise EmailAlreadyExistsError("User must register first")

        InvitationsService._attach_user_to_team(user, invitation)

        InvitationsRepository.update_status(invitation, invitation.STATUS_ACCEPTED)

    @staticmethod
    def register_user_by_invitation(token, data):
        invitation = InvitationsService.get_invitation_by_token(token)

        if data["email"] != invitation.email:
            raise InvitationEmailMismatchError("Email does not match invitation")

        if UserService.exists_by_email(data["email"]):
            raise EmailAlreadyExistsError("User already exists")

        user = UserService.create_user(
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







"""import uuid
import os
from typing import Tuple, List

from django.db import transaction

from modules.invitations.domain.models import Invitation
from modules.invitations.repository.invitations_repository import InvitationsRepository
from modules.invitations.domain.exceptions import (
    InvitationNotFoundError,
    InvitationInvalidError,
    InvitationEmailMismatchError,
    EmailAlreadyExistsError,
)
from modules.users.domain.models import User
from modules.users.domain.exceptions import UserNotFoundError
from modules.users.repository.users_repository import UsersRepository
from modules.teams.domain.models import Team, Role, UserTeam


class InvitationsService:
    """
    Service layer for Invitations module.
    """

    @staticmethod
    def _build_invite_url(token: uuid.UUID) -> str:
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        frontend_url = frontend_url.rstrip("/")
        return f"{frontend_url}/invite/{token}"

    # ---------- CREATE ----------

    @staticmethod
    def create_invitation(
        team_id,
        created_by: User,
        dto: dict,
    ) -> Tuple[Invitation, str]:
        """
        Creates invitation and returns (invitation, invite_url).
        """
        team = Team.objects.filter(id=team_id, deleted_at__isnull=True).first()
        if not team:
            raise InvitationInvalidError("Team not found or soft-deleted")

        email = dto["email"]
        single_use = dto.get("singleUse", True)
        is_captain = dto.get("isCaptain", False)
        has_permission_manage_users = dto.get("hasPermissionManageUsers", False)
        has_permission_manage_projects = dto.get("hasPermissionManageProjects", False)

        invitation = InvitationsRepository.create(
            team=team,
            email=email,
            single_use=single_use,
            is_captain=is_captain,
            has_permission_manage_users=has_permission_manage_users,
            has_permission_manage_projects=has_permission_manage_projects,
            created_by=created_by,
        )

        invite_url = InvitationsService._build_invite_url(invitation.token)
        return invitation, invite_url

    # ---------- GET BY TOKEN ----------

    @staticmethod
    def _ensure_team_active(invitation: Invitation) -> None:
        team = invitation.team
        if not team or team.deleted_at is not None:
            raise InvitationInvalidError("Team is deleted or inactive")

    @staticmethod
    def get_invitation_by_token(token: str) -> Invitation:
        """
        Full validation: existence, team active, status == pending.
        """
        invitation = InvitationsRepository.find_by_token(token)
        if not invitation:
            raise InvitationNotFoundError("Invitation not found")

        InvitationsService._ensure_team_active(invitation)

        if invitation.status != Invitation.STATUS_PENDING:
            raise InvitationInvalidError("Invitation is not pending")

        return invitation

    @staticmethod
    def get_invitation_by_token_without_status_check(token: str) -> Invitation:
        """
        Used for public/info endpoints: ignores status, but checks existence and team activity.
        """
        invitation = InvitationsRepository.find_by_token(token)
        if not invitation:
            raise InvitationNotFoundError("Invitation not found")

        InvitationsService._ensure_team_active(invitation)
        return invitation

    # ---------- USER CHECK ----------

    @staticmethod
    def check_user_exists(email: str) -> bool:
        user = UsersRepository.get_by_email(email)
        return user is not None

    # ---------- ATTACH USER TO TEAM (internal helper) ----------

    @staticmethod
    @transaction.atomic
    def _attach_user_to_team(invitation: Invitation, user: User) -> None:
        """
        Creates/updates UserTeam and optional Captain role.
        """
        team = invitation.team

        # base permissions from invite flags
        perm_manage_users = invitation.has_permission_manage_users
        perm_manage_projects = invitation.has_permission_manage_projects

        # captain implies full permissions
        if invitation.is_captain:
            perm_manage_users = True
            perm_manage_projects = True

        user_team, created = UserTeam.objects.get_or_create(
            user=user,
            team=team,
            defaults={
                "has_permission_manage_users": perm_manage_users,
                "has_permission_manage_projects": perm_manage_projects,
            },
        )

        if not created:
            # обновляем права, если приглашение даёт больше
            if perm_manage_users and not user_team.has_permission_manage_users:
                user_team.has_permission_manage_users = True
            if perm_manage_projects and not user_team.has_permission_manage_projects:
                user_team.has_permission_manage_projects = True
            user_team.save()

        if invitation.is_captain:
            Role.objects.get_or_create(
                user=user,
                team=team,
                defaults={"role": "captain"},
            )

    # ---------- ACCEPT INVITATION (existing user) ----------

    @staticmethod
    @transaction.atomic
    def accept_invitation(token: str) -> None:
        """
        Accept invitation for an already registered user.
        """
        invitation = InvitationsService.get_invitation_by_token(token)

        user = UsersRepository.get_by_email(invitation.email)
        if not user:
            raise UserNotFoundError(f"User with email={invitation.email} not found")

        # check if already in team
        in_team = UserTeam.objects.filter(
            user=user,
            team=invitation.team,
            deleted_at__isnull=True,
        ).exists()

        if in_team:
            # если singleUse — просто пометить accepted
            if invitation.single_use and invitation.status != Invitation.STATUS_ACCEPTED:
                invitation.status = Invitation.STATUS_ACCEPTED
                invitation.save(update_fields=["status"])
            return

        InvitationsService._attach_user_to_team(invitation, user)

        if invitation.single_use:
            invitation.status = Invitation.STATUS_ACCEPTED
            invitation.save(update_fields=["status"])

    # ---------- REGISTER USER BY INVITATION ----------

    @staticmethod
    @transaction.atomic
    def register_user_by_invitation(token: str, dto: dict) -> User:
        """
        Register new user from invitation token and attach to team.
        """
        invitation = InvitationsService.get_invitation_by_token(token)

        email = dto["email"]
        if email.lower() != invitation.email.lower():
            raise InvitationEmailMismatchError("Email does not match invitation email")

        existing = UsersRepository.get_by_email(email)
        if existing:
            raise EmailAlreadyExistsError("User with this email already exists")

        password = dto["password"]
        first_name = dto.get("firstName", "")
        last_name = dto.get("lastName", "")

        # создаём пользователя через менеджер
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        InvitationsService._attach_user_to_team(invitation, user)

        if invitation.single_use:
            invitation.status = Invitation.STATUS_ACCEPTED
            invitation.save(update_fields=["status"])

        return user

    # ---------- CANCEL INVITATION ----------

    @staticmethod
    def cancel_invitation(invitation_id: str) -> None:
        invitation = InvitationsRepository.find_by_id(invitation_id)
        if not invitation:
            raise InvitationNotFoundError("Invitation not found")

        if invitation.status == Invitation.STATUS_CANCELLED:
            return

        invitation.status = Invitation.STATUS_CANCELLED
        invitation.save(update_fields=["status"])

    # ---------- LIST TEAM INVITATIONS ----------

    @staticmethod
    def get_team_invitations(team_id) -> List[Invitation]:
        return list(InvitationsRepository.find_by_team_id(team_id))
"""