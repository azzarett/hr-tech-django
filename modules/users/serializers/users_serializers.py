from rest_framework import serializers
from modules.users.domain.models import User


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ["password", "is_superuser", "is_active", "is_staff", "deleted_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
