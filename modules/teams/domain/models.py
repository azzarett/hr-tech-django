import uuid
from django.db import models


USER_ROLE_CHOICES = (
    ("captain", "captain"),
    ("vice-captain", "vice-captain"),
    ("developer", "developer"),
    ("designer", "designer"),
    ("pm", "pm"),
    ("pr", "pr"),
    ("hr", "hr"),
    ("business-adviser", "business-adviser"),
    ("academic-adviser", "academic-adviser"),
    ("marketer", "marketer"),
    ("event-manager", "event-manager"),
)


class Team(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    educational_institution_type = models.CharField(max_length=255)
    city_id = models.UUIDField()
    university_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "teams"
        db_table = "teams"

    def __str__(self):
        return self.name


class Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="roles",
    )
    team = models.ForeignKey(
        "teams.Team",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="roles",
    )
    role = models.CharField(max_length=64, choices=USER_ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "teams"
        db_table = "roles"

    def __str__(self):
        user_value = getattr(self, "user_id", None) or getattr(self.user, "id", None)
        return f"{user_value} - {self.role}"


class UserTeam(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="user_teams",
    )
    team = models.ForeignKey(
        "teams.Team",
        on_delete=models.CASCADE,
        related_name="user_teams",
    )
    has_permission_manage_users = models.BooleanField(default=False)
    has_permission_manage_projects = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "teams"
        db_table = "user_teams"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "team"], name="unique_user_team_membership"
            )
        ]

    def __str__(self):
        user_value = getattr(self, "user_id", None) or getattr(self.user, "id", None)
        team_value = getattr(self, "team_id", None) or getattr(self.team, "id", None)
        return f"{user_value} - {team_value}"
