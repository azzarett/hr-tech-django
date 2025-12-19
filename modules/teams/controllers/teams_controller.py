from typing import Any, Dict

from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from modules.teams.domain.models import Team
from modules.teams.serializers.teams_serializers import TeamSerializer


class TeamsController(ViewSet):
    permission_classes = [permissions.AllowAny]

    def list(self, request: Request) -> Response:
        teams = Team.objects.filter(deleted_at__isnull=True)
        return Response({"teams": TeamSerializer(teams, many=True).data})

    def retrieve(self, request: Request, pk: str | None = None) -> Response:
        try:
            team = Team.objects.get(id=pk, deleted_at__isnull=True)
        except Team.DoesNotExist:
            return Response({"detail": "Team not found"}, status=404)
        return Response({"team": TeamSerializer(team).data})

    def create(self, request: Request) -> Response:
        # Игнорируем read_only_fields — вручную достаем нужные поля
        payload: Dict[str, Any] = request.data

        team = Team.objects.create(
            name=payload.get("name"),
            educational_institution_type=payload.get("educational_institution_type"),
            city_id=payload.get("city_id"),
            university_id=payload.get("university_id"),
        )

        return Response({"team": TeamSerializer(team).data}, status=201)
