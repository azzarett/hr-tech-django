from django.urls import path

from modules.invitations.controllers.invitations_controller import (
    TeamInvitationsView,
    InvitationByTokenView,
    InvitationCheckUserView,
    AcceptInvitationView,
    RegisterUserByInvitationView,
    CancelInvitationView,
    AllInvitationsView,
)

urlpatterns = [
    path(
        "teams/<uuid:team_id>/invitations",
        TeamInvitationsView.as_view(),
        name="team-invitations"
    ),
    
    path(
        "invitations",
        AllInvitationsView.as_view(),
        name="all-invitations"
    ),

    path(
        "invitations/<uuid:token>",
        InvitationByTokenView.as_view(),
        name="invitation-by-token"
    ),

    path(
        "invitations/<uuid:token>/check-user",
        InvitationCheckUserView.as_view(),
        name="invitation-check-user"
    ),

    # Short route for frontend compatibility
    path(
        "accept",
        AcceptInvitationView.as_view(),
        name="accept-invitation-short"
    ),

    path(
        "invitations/accept",
        AcceptInvitationView.as_view(),
        name="invitation-accept"
    ),

    path(
        "invitations/<uuid:token>/register",
        RegisterUserByInvitationView.as_view(),
        name="invitation-register"
    ),

    path(
        "invitations/<uuid:id>/cancel",
        CancelInvitationView.as_view(),
        name="invitation-cancel"
    ),
]

