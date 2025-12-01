from rest_framework import serializers
from modules.invitations.domain.models import Invitation


class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = "__all__"


class CreateInvitationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    single_use = serializers.BooleanField(required=False, default=True)
    is_captain = serializers.BooleanField(required=False, default=False)
    has_permission_manage_users = serializers.BooleanField(required=False, default=False)
    has_permission_manage_projects = serializers.BooleanField(required=False, default=False)


class AcceptInvitationSerializer(serializers.Serializer):
    token = serializers.CharField()


class RegisterUserByInvitationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()



"""from rest_framework import serializers
from modules.invitations.domain.models import Invitation


class InvitationSerializer(serializers.ModelSerializer):
    singleUse = serializers.BooleanField(source="single_use")
    isCaptain = serializers.BooleanField(source="is_captain")
    hasPermissionManageUsers = serializers.BooleanField(source="has_permission_manage_users")
    hasPermissionManageProjects = serializers.BooleanField(source="has_permission_manage_projects")
    createdBy = serializers.IntegerField(source="created_by_id", read_only=True)
    teamId = serializers.IntegerField(source="team_id", read_only=True)

    class Meta:
        model = Invitation
        fields = [
            "id",
            "email",
            "token",
            "status",
            "singleUse",
            "isCaptain",
            "hasPermissionManageUsers",
            "hasPermissionManageProjects",
            "createdBy",
            "teamId",
            "created_at",
        ]


class CreateInvitationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    singleUse = serializers.BooleanField(required=False, default=True)
    isCaptain = serializers.BooleanField(required=False, default=False)
    hasPermissionManageUsers = serializers.BooleanField(required=False, default=False)
    hasPermissionManageProjects = serializers.BooleanField(required=False, default=False)


class AcceptInvitationSerializer(serializers.Serializer):
    token = serializers.CharField()


class RegisterUserByInvitationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    firstName = serializers.CharField(required=False, allow_blank=True)
    lastName = serializers.CharField(required=False, allow_blank=True)
"""