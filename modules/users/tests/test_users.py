from __future__ import annotations

import uuid
from typing import Dict

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from modules.teams.domain.models import Role, Team, UserTeam
from modules.users.domain.models import User, UserAuthToken


class UsersApiTests(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()

        self.team = Team.objects.create(
            name="Team A",
            educational_institution_type="university",
            city_id="11111111-1111-1111-1111-111111111111",
            university_id=None,
        )

        self.user = User.objects.create_user(  # type: ignore
            email="user@example.com",
            password="secret123",
            first_name="User",
            last_name="One",
        )
        self.token = self._issue_token(self.user)

        self.other_user = User.objects.create_user(  # type: ignore
            email="other@example.com",
            password="secret123",
            first_name="Other",
            last_name="User",
        )

        # Current user is captain and member of team
        UserTeam.objects.create(
            user=self.user, team=self.team, has_permission_manage_users=True)
        Role.objects.create(user=self.user, team=self.team, role="captain")

        # Other user is member of team
        UserTeam.objects.create(
            user=self.other_user, team=self.team, has_permission_manage_users=False)

    def _issue_token(self, user: User) -> str:
        token_obj = UserAuthToken.objects.create(
            user=user, token="token-" + user.email)
        return token_obj.token

    def _auth(self, token: str | None = None) -> APIClient:
        client = APIClient()
        if token:
            client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return client

    # ---------- /v1/users/token ----------
    def test_token_success(self) -> None:
        res = self.client.post(
            "/v1/users/token",
            {"email": "user@example.com", "password": "secret123"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("auth", res.data)
        self.assertIn("token", res.data["auth"])

    def test_token_wrong_password(self) -> None:
        res = self.client.post(
            "/v1/users/token",
            {"email": "user@example.com", "password": "wrong"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_user_not_found(self) -> None:
        res = self.client.post(
            "/v1/users/token",
            {"email": "absent@example.com", "password": "secret"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_token_inactive_user(self) -> None:
        User.objects.create_user(  # type: ignore
            email="inactive@example.com",
            password="secret123",
            first_name="In",
            last_name="Active",
            is_active=False,
        )
        res = self.client.post(
            "/v1/users/token",
            {"email": "inactive@example.com", "password": "secret123"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    # ---------- /v1/users/me ----------
    def test_me_success(self) -> None:
        res = self._auth(self.token).get("/v1/users/me")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["user"]["email"], "user@example.com")

    def test_me_missing_token(self) -> None:
        res = self.client.get("/v1/users/me")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_invalid_token(self) -> None:
        res = self._auth("invalid").get("/v1/users/me")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    # ---------- /v1/users list ----------
    def test_users_list_success(self) -> None:
        res = self._auth(self.token).get(f"/v1/users?team_id={self.team.id}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.data["users"]), 1)

    def test_users_list_missing_team_returns_empty(self) -> None:
        res = self._auth(self.token).get("/v1/users")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["users"], [])

    def test_users_list_invalid_token(self) -> None:
        res = self._auth("invalid").get(f"/v1/users?team_id={self.team.id}")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    # ---------- /v1/users/me/update ----------
    def test_update_me_success(self) -> None:
        payload: Dict[str, str] = {"city": "Almaty"}
        res = self._auth(self.token).patch(
            f"/v1/users/me/update?team_id={self.team.id}", payload, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.city, "Almaty")

    def test_update_me_missing_team_id(self) -> None:
        res = self._auth(self.token).patch(
            "/v1/users/me/update",
            {"city": "Astana"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # ---------- /v1/users/<id> DELETE ----------
    def test_destroy_user_success_with_permission(self) -> None:
        res = self._auth(self.token).delete(
            f"/v1/users/{self.other_user.id}?team_id={self.team.id}"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        membership = UserTeam.objects.filter(
            user=self.other_user, team=self.team).first()
        self.assertIsNotNone(membership)
        self.assertIsNotNone(membership.deleted_at)

    def test_destroy_user_forbidden_without_permission(self) -> None:
        UserTeam.objects.filter(user=self.user, team=self.team).update(
            has_permission_manage_users=False)
        Role.objects.filter(user=self.user, team=self.team).update(
            role="developer")

        res = self._auth(self.token).delete(
            f"/v1/users/{self.other_user.id}?team_id={self.team.id}"
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_destroy_user_missing_team_id(self) -> None:
        res = self._auth(self.token).delete(f"/v1/users/{self.other_user.id}")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class InvitationsApiTests(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.team = Team.objects.create(
            name="Team B",
            educational_institution_type="university",
            city_id="22222222-2222-2222-2222-222222222222",
            university_id=None,
        )
        self.creator = User.objects.create_user(  # type: ignore
            email="creator@example.com",
            password="secret123",
            first_name="Creator",
            last_name="User",
        )
        self.creator_token = UserAuthToken.objects.create(
            user=self.creator, token="creator-token"
        ).token

    def _auth(self, token: str | None = None) -> APIClient:
        client = APIClient()
        if token:
            client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return client

    def test_create_invitation_success(self) -> None:
        payload = {"email": "invitee@example.com"}
        res = self._auth(self.creator_token).post(
            f"/v1/teams/{self.team.id}/invitations", payload, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("invitation", res.data)

    def test_create_invitation_missing_token(self) -> None:
        res = self.client.post(
            f"/v1/teams/{self.team.id}/invitations",
            {"email": "invitee@example.com"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_team_invitations_requires_token(self) -> None:
        res = self.client.get(f"/v1/teams/{self.team.id}/invitations")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_team_invitations_success(self) -> None:
        self._auth(self.creator_token).post(
            f"/v1/teams/{self.team.id}/invitations",
            {"email": "invitee@example.com"},
            format="json",
        )
        res = self._auth(self.creator_token).get(
            f"/v1/teams/{self.team.id}/invitations")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.data["invitations"]), 1)

    def test_accept_invitation_not_found(self) -> None:
        res = self.client.post(
            "/v1/accept", {"token": str(uuid.uuid4())}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_register_user_by_invitation_success(self) -> None:
        invitation = self._auth(self.creator_token).post(
            f"/v1/teams/{self.team.id}/invitations",
            {"email": "newuser@example.com"},
            format="json",
        ).data["invitation"]

        res = self.client.post(
            f"/v1/invitations/{invitation['token']}/register",
            {
                "email": "newuser@example.com",
                "password": "secret123",
                "first_name": "New",
                "last_name": "User",
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(
            email="newuser@example.com").exists())

    def test_register_user_by_invitation_email_mismatch(self) -> None:
        invitation = self._auth(self.creator_token).post(
            f"/v1/teams/{self.team.id}/invitations",
            {"email": "expect@example.com"},
            format="json",
        ).data["invitation"]

        res = self.client.post(
            f"/v1/invitations/{invitation['token']}/register",
            {
                "email": "other@example.com",
                "password": "secret123",
                "first_name": "New",
                "last_name": "User",
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cancel_invitation_success(self) -> None:
        invitation_id = self._auth(self.creator_token).post(
            f"/v1/teams/{self.team.id}/invitations",
            {"email": "cancelme@example.com"},
            format="json",
        ).data["invitation"]["id"]

        res = self._auth(self.creator_token).patch(
            f"/v1/invitations/{invitation_id}/cancel")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_cancel_invitation_missing_token(self) -> None:
        invitation_id = self._auth(self.creator_token).post(
            f"/v1/teams/{self.team.id}/invitations",
            {"email": "cancelme@example.com"},
            format="json",
        ).data["invitation"]["id"]

        res = self.client.patch(f"/v1/invitations/{invitation_id}/cancel")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_invitations_requires_token(self) -> None:
        res = self.client.get("/v1/invitations")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_invitations_success(self) -> None:
        self._auth(self.creator_token).post(
            f"/v1/teams/{self.team.id}/invitations",
            {"email": "list@example.com"},
            format="json",
        )
        res = self._auth(self.creator_token).get("/v1/invitations")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsInstance(res.data.get("invitations"), list)


class TeamsApiTests(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.team = Team.objects.create(
            name="Team C",
            educational_institution_type="college",
            city_id="33333333-3333-3333-3333-333333333333",
            university_id=None,
        )

    def test_teams_list(self) -> None:
        res = self.client.get("/v1/teams")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.data.get("teams", [])), 1)

    def test_team_retrieve_not_found(self) -> None:
        res = self.client.get("/v1/teams/00000000-0000-0000-0000-000000000000")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
