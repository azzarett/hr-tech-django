from __future__ import annotations

from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import View


class IsBearerAuthenticated(permissions.BasePermission):
	"""Allows access only to users authenticated via Bearer tokens and still active."""

	message = "Authentication credentials were not provided or are invalid."

	def has_permission(self, request: Request, view: View) -> bool:
		user = getattr(request, "user", None)
		return bool(user and user.is_authenticated)
