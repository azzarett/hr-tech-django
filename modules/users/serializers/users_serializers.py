from rest_framework import serializers

from modules.teams.serializers.teams_serializers import (
    RoleSerializer,
    TeamSerializer,
    UserTeamSerializer,
)
from modules.users.domain.models import User


class UsersSerializer(serializers.ModelSerializer):
    teams = TeamSerializer(many=True, read_only=True)
    roles = RoleSerializer(many=True, read_only=True)
    user_teams = UserTeamSerializer(many=True, read_only=True)

    class Meta:
        model = User
        exclude = ["password", "is_superuser", "is_active", "is_staff", "deleted_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
