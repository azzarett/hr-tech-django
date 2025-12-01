from modules.invitations.domain.models import Invitation


class InvitationsRepository:

    @staticmethod
    def create(**data):
        return Invitation.objects.create(**data)

    @staticmethod
    def find_by_token(token):
        try:
            return Invitation.objects.select_related("team", "created_by").get(token=token)
        except Invitation.DoesNotExist:
            return None

    @staticmethod
    def find_by_id(id):
        try:
            return Invitation.objects.select_related("team", "created_by").get(id=id)
        except Invitation.DoesNotExist:
            return None

    @staticmethod
    def update_status(invitation, status):
        invitation.status = status
        invitation.save()
        return invitation

    @staticmethod
    def find_by_team_id(team_id):
        return Invitation.objects.filter(team_id=team_id).order_by("-created_at")









"""from modules.invitations.domain.models import Invitation
from django.db.models import Prefetch
from django.core.exceptions import ObjectDoesNotExist


class InvitationsRepository:

    @staticmethod
    def create(**data) -> Invitation:
        """
        Создаёт приглашение и возвращает объект модели.
        """
        invitation = Invitation.objects.create(**data)
        return invitation

    @staticmethod
    def find_by_token(token: str) -> Invitation | None:
        """
        Ищет инвайт по токену, с подгрузкой команды.
        Команда не должна быть soft-deleted.
        """
        try:
            return Invitation.objects.select_related("team", "created_by").get(token=token)
        except Invitation.DoesNotExist:
            return None

    @staticmethod
    def find_by_id(invitation_id: str) -> Invitation | None:
        """
        Находит приглашение по id.
        """
        try:
            return Invitation.objects.select_related("team", "created_by").get(id=invitation_id)
        except Invitation.DoesNotExist:
            return None

    @staticmethod
    def update_status(invitation_id: str, status: str) -> bool:
        """
        Обновляет статус приглашения.
        """
        updated = Invitation.objects.filter(id=invitation_id).update(status=status)
        return updated > 0

    @staticmethod
    def find_by_team_id(team_id: str):
        """
        Возвращает все приглашения команды, отсортированные по дате создания.
        """
        return (
            Invitation.objects
            .filter(team_id=team_id)
            .select_related("team", "created_by")
            .order_by("-created_at")
        )"""
