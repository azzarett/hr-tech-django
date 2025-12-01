from django.urls import path
from modules.users.controllers.users_controller import UsersController

users = UsersController.as_view

urlpatterns = [
    path("token/", users({"post": "token"})),
    path("me/", users({"get": "me"})),
    path("<uuid:pk>/", users({"get": "retrieve"})),
]
