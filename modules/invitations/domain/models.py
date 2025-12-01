import uuid
from django.db import models
from django.utils import timezone
from modules.teams.domain.models import Team
from modules.users.domain.models import User


class Invitation(models.Model):
    STATUS_PENDING = "pending"
    STATUS_ACCEPTED = "accepted"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="invitations")
    email = models.EmailField()

    token = models.UUIDField(default=uuid.uuid4, unique=True)
    single_use = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    is_captain = models.BooleanField(default=False)
    has_permission_manage_users = models.BooleanField(default=False)
    has_permission_manage_projects = models.BooleanField(default=False)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_invitations")

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.email} -> {self.team.name} ({self.status})"









"""import uuid
from django.db import models


class Invitation(models.Model):
    STATUS_PENDING = "pending"
    STATUS_ACCEPTED = "accepted"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = (
        (STATUS_PENDING, "pending"),
        (STATUS_ACCEPTED, "accepted"),
        (STATUS_CANCELLED, "cancelled"),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    team = models.ForeignKey(
        "teams.Team",
        on_delete=models.CASCADE,
        related_name="invitations",
    )
    email = models.EmailField()
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    single_use = models.BooleanField(default=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    is_captain = models.BooleanField(default=False)
    has_permission_manage_users = models.BooleanField(default=False)
    has_permission_manage_projects = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="created_invitations",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "invitations"
        app_label = "invitations"

    def __str__(self) -> str:
        return f"{self.email} → team {self.team_id}"""
