from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status, permissions

from modules.users.services.auth_service import AuthService

from modules.invitations.services.invitations_service import InvitationsService
from modules.invitations.serializers.invitations_serializers import (
    InvitationSerializer,
    CreateInvitationSerializer,
    AcceptInvitationSerializer,
    RegisterUserByInvitationSerializer,
)
from modules.invitations.domain.exceptions import (
    InvitationNotFoundError,
    InvitationInvalidError,
    InvitationEmailMismatchError,
    EmailAlreadyExistsError,
)
from modules.users.domain.exceptions import UserNotFoundError


def _handle_invitation_errors(exc: Exception):
    if isinstance(exc, InvitationNotFoundError):
        return Response({"detail": "Invitation not found"}, status=404)

    if isinstance(exc, (InvitationInvalidError, InvitationEmailMismatchError, EmailAlreadyExistsError)):
        return Response({"detail": str(exc)}, status=400)

    if isinstance(exc, UserNotFoundError):
        return Response({"detail": str(exc)}, status=400)

    raise exc


# ============================
#   TEAM INVITATIONS
# ============================
class TeamInvitationsView(APIView):
    """
    POST /v1/teams/<team_id>/invitations
    GET  /v1/teams/<team_id>/invitations
    """
    permission_classes = [AllowAny]

    def post(self, request, team_id):
        # 1. Validate Bearer token
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return Response({"detail": "Authentication credentials were not provided."}, status=401)

        token_str = auth_header.split(" ")[1]
        token_data = AuthService.validate_token(token_str)
        if not token_data:
            return Response({"detail": "Invalid token"}, status=401)

        user = token_data["user"]

        # 2. Validate body
        serializer = CreateInvitationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dto = serializer.validated_data

        # 3. Create invitation
        try:
            invitation, invite_url = InvitationsService.create_invitation(
                team_id=team_id,
                created_by=user,
                dto=dto,
            )
        except Exception as exc:
            return _handle_invitation_errors(exc)

        return Response(
            {
                "invitation": InvitationSerializer(invitation).data,
                "inviteUrl": invite_url,
            },
            status=201,
        )

    def get(self, request, team_id):
        # Auth via Bearer
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return Response({"detail": "Authentication credentials were not provided."}, status=401)

        token_str = auth_header.split(" ")[1]
        if not AuthService.validate_token(token_str):
            return Response({"detail": "Invalid token"}, status=401)

        invitations = InvitationsService.get_team_invitations(team_id)
        return Response({"invitations": InvitationSerializer(invitations, many=True).data}, status=200)


# ============================
#   PUBLIC ENDPOINTS
# ============================
class InvitationByTokenView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        try:
            invitation = InvitationsService.get_invitation_by_token_without_status_check(
                token)
        except Exception as exc:
            resp = _handle_invitation_errors(exc)
            if resp:
                return resp

        return Response({"invitation": InvitationSerializer(invitation).data}, status=200)


class InvitationCheckUserView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        try:
            invitation = InvitationsService.get_invitation_by_token_without_status_check(
                token)
            user_exists = InvitationsService.check_user_exists(
                invitation.email)
        except Exception as exc:
            resp = _handle_invitation_errors(exc)
            if resp:
                return resp

        return Response(
            {
                "userExists": user_exists,
                "email": invitation.email,
            },
            status=200,
        )


# ============================
#   ACCEPT INVITATION
# ============================
class AcceptInvitationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AcceptInvitationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]

        try:
            InvitationsService.accept_invitation(token)
        except Exception as exc:
            resp = _handle_invitation_errors(exc)
            if resp:
                return resp

        return Response(status=204)


# ============================
#   REGISTER BY INVITATION
# ============================
class RegisterUserByInvitationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, token):
        serializer = RegisterUserByInvitationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            InvitationsService.register_user_by_invitation(
                token, serializer.validated_data)
        except Exception as exc:
            resp = _handle_invitation_errors(exc)
            if resp:
                return resp

        return Response(
            {"message": "Пользователь успешно зарегистрирован"},
            status=201,
        )


# ============================
#   CANCEL INVITATION
# ============================
class CancelInvitationView(APIView):
    permission_classes = [AllowAny]

    def patch(self, request, id):
        # Auth via Bearer
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return Response({"detail": "Authentication credentials were not provided."}, status=401)

        token_str = auth_header.split(" ")[1]
        if not AuthService.validate_token(token_str):
            return Response({"detail": "Invalid token"}, status=401)

        try:
            InvitationsService.cancel_invitation(id)
        except Exception as exc:
            resp = _handle_invitation_errors(exc)
            if resp:
                return resp

        return Response({"message": "Приглашение отменено"}, status=200)


# ============================
#   ALL INVITATIONS (for current user)
# ============================
class AllInvitationsView(APIView):
    """
    GET /v1/invitations - get all invitations (optionally filtered by team_id)
    """
    permission_classes = [AllowAny]

    def get(self, request):
        # Auth via Bearer
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return Response({"detail": "Authentication credentials were not provided."}, status=401)

        token_str = auth_header.split(" ")[1]
        if not AuthService.validate_token(token_str):
            return Response({"detail": "Invalid token"}, status=401)

        team_id = request.query_params.get("team_id")
        
        if team_id:
            invitations = InvitationsService.get_team_invitations(team_id)
        else:
            # Return empty list if no team_id provided
            invitations = []

        return Response({"invitations": InvitationSerializer(invitations, many=True).data}, status=200)
