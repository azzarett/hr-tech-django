from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status, permissions

from modules.teams.domain.models import Team
from modules.teams.serializers.teams_serializers import TeamSerializer


class TeamsController(ViewSet):
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        teams = Team.objects.filter(deleted_at__isnull=True)
        return Response({"teams": TeamSerializer(teams, many=True).data})

    def retrieve(self, request, pk=None):
        try:
            team = Team.objects.get(id=pk, deleted_at__isnull=True)
        except Team.DoesNotExist:
            return Response({"detail": "Team not found"}, status=404)
        return Response({"team": TeamSerializer(team).data})

    def create(self, request):
        # Игнорируем read_only_fields — вручную достаем нужные поля
        payload = request.data

        team = Team.objects.create(
            name=payload.get("name"),
            educational_institution_type=payload.get("educational_institution_type"),
            city_id=payload.get("city_id"),
            university_id=payload.get("university_id"),
        )

        return Response({"team": TeamSerializer(team).data}, status=201)
