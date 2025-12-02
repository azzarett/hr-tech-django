from modules.invitations.domain.models import Invitation


class InvitationsRepository:

    @staticmethod
    def _base_queryset():
        return Invitation.objects.select_related("team", "created_by").filter(deleted_at__isnull=True)

    @staticmethod
    def create(**data):
        return Invitation.objects.create(**data)

    @staticmethod
    def find_by_token(token):
        try:
            return InvitationsRepository._base_queryset().get(token=token)
        except Invitation.DoesNotExist:
            return None

    @staticmethod
    def find_by_id(id):
        try:
            return InvitationsRepository._base_queryset().get(id=id)
        except Invitation.DoesNotExist:
            return None

    @staticmethod
    def update_status(invitation, status):
        invitation.status = status
        invitation.save()
        return invitation

    @staticmethod
    def find_by_team_id(team_id):
        return InvitationsRepository._base_queryset().filter(team_id=team_id).order_by("-created_at")
