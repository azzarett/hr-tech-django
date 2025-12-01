from django.urls import path
from modules.teams.controllers.teams_controller import TeamsController

teams = TeamsController.as_view

urlpatterns = [
    path("", teams({"get": "list", "post": "create"})),
    path("<uuid:pk>", teams({"get": "retrieve"})),
]
