from rest_framework import serializers
from modules.invitations.domain.models import Invitation
from modules.teams.serializers.teams_serializers import TeamSerializer


class InvitationSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)

    class Meta:
        model = Invitation
        fields = (
            "id",
            "team_id",
            "team",
            "email",
            "token",
            "single_use",
            "is_captain",
            "status",
            "created_by",
            "created_at",
        )
        read_only_fields = fields


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
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    firstName = serializers.CharField(required=False, write_only=True)
    lastName = serializers.CharField(required=False, write_only=True)

    def validate(self, data):
        # Support both camelCase and snake_case
        if 'firstName' in data:
            data['first_name'] = data.pop('firstName')
        if 'lastName' in data:
            data['last_name'] = data.pop('lastName')
        
        # Ensure required fields are present
        if not data.get('first_name'):
            raise serializers.ValidationError({"first_name": "This field is required."})
        if not data.get('last_name'):
            raise serializers.ValidationError({"last_name": "This field is required."})
        
        return data
