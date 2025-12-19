from __future__ import annotations

from typing import Optional

from django.db.models import Prefetch, QuerySet

from modules.teams.domain.models import Role, Team, UserTeam
from modules.users.domain.models import User


class UsersRepository:

    @staticmethod
    def _base_queryset() -> QuerySet[User]:
        roles_qs = Role.objects.filter(deleted_at__isnull=True).select_related("team")
        user_teams_qs = (
            UserTeam.objects.filter(deleted_at__isnull=True)
            .select_related("team")
        )
        teams_qs = Team.objects.filter(deleted_at__isnull=True)

        return (
            User.objects.filter(deleted_at__isnull=True)
            .prefetch_related(
                Prefetch("roles", queryset=roles_qs),
                Prefetch("user_teams", queryset=user_teams_qs),
                Prefetch("teams", queryset=teams_qs),
            )
        )

    @staticmethod
    def get_by_id(user_id: str | None) -> Optional[User]:
        return UsersRepository._base_queryset().filter(id=user_id).first()

    @staticmethod
    def get_by_email(email: str) -> Optional[User]:
        return UsersRepository._base_queryset().filter(email=email).first()

    @staticmethod
    def save(user: User) -> User:
        user.save()
        return user
