from rest_framework import serializers

from modules.teams.domain.models import Role, Team, UserTeam


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = (
            "id",
            "name",
            "educational_institution_type",
            "city_id",
            "university_id",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class RoleSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)

    class Meta:
        model = Role
        fields = (
            "id",
            "role",
            "team",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class UserTeamSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)

    class Meta:
        model = UserTeam
        fields = (
            "id",
            "has_permission_manage_users",
            "has_permission_manage_projects",
            "team",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
